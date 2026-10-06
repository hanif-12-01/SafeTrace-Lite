"""Atomic software specification of selected proposal behavior.

Serialization, sequence consumption and genesis are model conventions.
No RTL, timing, trusted Python execution, or production key storage is modeled.
"""

from dataclasses import dataclass
from enum import IntEnum
import hashlib
import hmac
import struct
from typing import Sequence

MAX_COUNTER = (1 << 32) - 1
EVENT_FORMAT = struct.Struct('>IIBHHBH')
COMMAND_FORMAT = struct.Struct('>BHI')


def _uint(value: int, bits: int, name: str) -> None:
    if type(value) is not int or not 0 <= value < (1 << bits):
        raise ValueError(f'{name} must be an unsigned {bits}-bit integer')


class Reason(IntEnum):
    OK = 0
    UNTRUSTED = 1
    AUTH_FAIL = 2
    REPLAY = 3
    POLICY = 4
    DIGEST_MISMATCH = 5
    ROLLBACK = 6


@dataclass(frozen=True)
class Configuration:
    trusted_digest: bytes
    key: bytes
    min_version: int
    max_speed: int = 80
    max_temperature: int = 70  # Example test fixture, not a proposal requirement.

    def __post_init__(self) -> None:
        if not isinstance(self.trusted_digest, bytes) or len(self.trusted_digest) != 32:
            raise ValueError('trusted_digest must be 32 bytes')
        if not isinstance(self.key, bytes) or len(self.key) != 32:
            raise ValueError('prototype key must be 32 bytes')
        _uint(self.min_version, 16, 'min_version')
        _uint(self.max_temperature, 16, 'max_temperature')
        _uint(self.max_speed, 16, 'max_speed')
        if self.max_speed > 100:
            raise ValueError('max_speed is a percentage from 0 to 100')


@dataclass(frozen=True)
class Command:
    command_id: int
    value: int
    sequence: int

    def __post_init__(self) -> None:
        _uint(self.command_id, 8, 'command_id')
        _uint(self.value, 16, 'value')
        _uint(self.sequence, 32, 'sequence')

    def payload(self) -> bytes:
        return COMMAND_FORMAT.pack(self.command_id, self.value, self.sequence)


def sign_command(key: bytes, command: Command) -> bytes:
    """Trusted sender/test helper; never a proposed host-accessible FPGA key API."""
    return hmac.new(key, command.payload(), hashlib.sha256).digest()


@dataclass(frozen=True)
class Decision:
    allow: bool
    reason: Reason


@dataclass(frozen=True)
class LogRecord:
    event: bytes
    chain_head: bytes


@dataclass(frozen=True)
class Checkpoint:
    device_id: str
    counter: int
    chain_head: bytes


@dataclass(frozen=True)
class Verification:
    valid: bool
    reason: str


def verify_log(records: Sequence[LogRecord], genesis: bytes, device_id: str,
               checkpoint: Checkpoint | None = None) -> Verification:
    """Check canonical records and an optionally trusted anchored prefix.

    Caller must obtain genesis/checkpoint independently from untrusted storage.
    An unanchored self-consistent chain cannot prove absence of tail deletion.
    """
    if not isinstance(genesis, bytes) or len(genesis) != 32:
        return Verification(False, 'INVALID_GENESIS')
    if checkpoint is not None:
        if checkpoint.device_id != device_id:
            return Verification(False, 'DEVICE_MISMATCH')
        if (type(checkpoint.counter) is not int or not 0 <= checkpoint.counter <= MAX_COUNTER
                or not isinstance(checkpoint.chain_head, bytes)
                or len(checkpoint.chain_head) != 32):
            return Verification(False, 'INVALID_CHECKPOINT')
        if len(records) < checkpoint.counter:
            return Verification(False, 'TRUNCATION')
    previous = genesis
    anchored_head = genesis if checkpoint is not None and checkpoint.counter == 0 else None
    for expected_counter, record in enumerate(records, 1):
        if not isinstance(record.event, bytes) or len(record.event) != EVENT_FORMAT.size:
            return Verification(False, 'INVALID_EVENT')
        if EVENT_FORMAT.unpack(record.event)[0] != expected_counter:
            return Verification(False, 'COUNTER_MISMATCH')
        current = hashlib.sha256(previous + record.event).digest()
        if not isinstance(record.chain_head, bytes) or not hmac.compare_digest(current, record.chain_head):
            return Verification(False, 'HASH_MISMATCH')
        previous = current
        if checkpoint is not None and expected_counter == checkpoint.counter:
            anchored_head = current
    if checkpoint is not None and not hmac.compare_digest(anchored_head, checkpoint.chain_head):
        return Verification(False, 'CHECKPOINT_MISMATCH')
    return Verification(True, 'OK')


class SafeTraceModel:
    """Within-epoch functional model; public attributes are not a security boundary."""

    def __init__(self, config: Configuration, device_id: str = 'demo-device') -> None:
        encoded_id = device_id.encode('utf-8')
        if not encoded_id or len(encoded_id) > 65535:
            raise ValueError('device_id must encode to 1..65535 bytes')
        self.config = config
        self.device_id = device_id
        self.reset()

    def reset(self) -> None:
        self.system_trusted = False
        self.actuator_enable = False
        self.boot_complete = False
        self.last_sequence = 0
        self.event_counter = 0
        self.version = 0
        self.genesis = bytes(32)
        self.chain_head = self.genesis
        self.records: list[LogRecord] = []
        self.tamper_flag = False

    def boot(self, image: bytes, version: int) -> Decision:
        if self.boot_complete:
            raise RuntimeError('boot once per reset epoch')
        self.actuator_enable = False
        _uint(version, 16, 'version')
        if not isinstance(image, bytes):
            raise ValueError('image must be bytes')
        digest = hashlib.sha256(image).digest()
        if not hmac.compare_digest(digest, self.config.trusted_digest):
            reason = Reason.DIGEST_MISMATCH
        elif version < self.config.min_version:
            reason = Reason.ROLLBACK
        else:
            reason = Reason.OK
        self.system_trusted = reason == Reason.OK
        self.version = version
        identity = self.device_id.encode('utf-8')
        material = (b'SafeTrace Lite software genesis v1\x00'
                    + struct.pack('>H', len(identity)) + identity + digest
                    + struct.pack('>HB', version, int(reason)))
        self.genesis = hashlib.sha256(material).digest()
        self.chain_head = self.genesis
        self.boot_complete = True
        return Decision(self.system_trusted, reason)  # Boot success is not actuation.

    def process(self, command: Command, tag: bytes, temperature: int,
                timestamp: int = 0) -> Decision:
        self.actuator_enable = False  # Fail closed, including malformed API input.
        _uint(temperature, 16, 'temperature')
        _uint(timestamp, 32, 'timestamp')
        if not isinstance(tag, bytes):
            raise ValueError('tag must be bytes')
        if not self.boot_complete:
            return Decision(False, Reason.UNTRUSTED)
        if self.event_counter == MAX_COUNTER:
            self.system_trusted = False
            raise OverflowError('event counter exhausted; no unlogged actuation')
        if not self.system_trusted:
            reason = Reason.UNTRUSTED
        elif not hmac.compare_digest(sign_command(self.config.key, command), tag):
            reason = Reason.AUTH_FAIL
        elif command.sequence <= self.last_sequence:
            reason = Reason.REPLAY
        else:
            # Software convention: consume fresh authenticated sequences on policy denial.
            self.last_sequence = command.sequence
            reason = (Reason.OK if command.command_id == 1
                      and command.value <= self.config.max_speed
                      and temperature <= self.config.max_temperature else Reason.POLICY)
        allow = reason == Reason.OK
        counter = self.event_counter + 1
        event = EVENT_FORMAT.pack(counter, timestamp, command.command_id,
                                  command.value, temperature,
                                  (0x80 if allow else 0) | int(reason), self.version)
        head = hashlib.sha256(self.chain_head + event).digest()
        self.records.append(LogRecord(event, head))
        self.event_counter = counter
        self.chain_head = head
        self.actuator_enable = allow
        return Decision(allow, reason)

    def checkpoint(self) -> Checkpoint:
        if not self.boot_complete:
            raise RuntimeError('no boot-bound audit epoch yet')
        return Checkpoint(self.device_id, self.event_counter, self.chain_head)

    def verify_stored_log(self, records: Sequence[LogRecord]) -> Verification:
        result = verify_log(records, self.genesis, self.device_id, self.checkpoint())
        if not result.valid:
            self.tamper_flag = True
        return result
