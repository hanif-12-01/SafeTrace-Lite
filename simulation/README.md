# Software Functional Reference Model

This directory contains an executable **software functional reference model**, using Python 3.10+ `hashlib`, `hmac`, `struct` and dataclasses. It is an executable specification for selected proposal behavior; it is not an FPGA emulator or RTL verification result.

From the repository root:

```sh
python -m unittest discover -s tests -v
python -m simulation.demo
```

The demo prints valid boot, safe command ALLOW, unsafe/replayed command BLOCK, a clean anchored log, and a modified log rejected. It uses an explicitly public fixture key constructed in memory; no real device credential is included.

## Implemented functional steps and integration roadmap

| Step | Software status | Planned hardware integration |
| --- | --- | --- |
| 1. Python functional reference | `reference_model.py` | Use as a cocotb oracle after canonical RTL formats are finalized. |
| 2. Boot integrity | Digest and minimum-version comparison, default-deny trust | Stream/pad image, share SHA, enforce protected configuration. |
| 3. HMAC authentication | Full SHA-256 tag over ID/value/sequence using `compare_digest` | Shared-core inner/outer hashing and complete tag comparison. |
| 4. Replay detection | Strictly increasing u32 sequence within a reset epoch | Define persistent/session semantics and atomic state updates. |
| 5. Safety policy | Speed command ID 1, inclusive speed/temperature limits | Comparator/FSM policy and coherent sensor sampling. |
| 6. SHA-256 chain | 16-byte event, boot-bound genesis and event counter | Fixed event packing, SHA scheduler and M10K/BRAM. |
| 7. Tamper detection | Stored-record/hash check plus independently retained checkpoint | FPGA verification path and HPS/backend checkpoint workflow. |
| 8. Future RTL integration | Planned | Verilator/ModelSim, cocotb, Avalon-MM wrapper, Quartus and SignalTap. |

## Model contract

`SafeTraceModel` receives an immutable configuration: trusted 32-byte image digest, 32-byte demo key, minimum version and policy limits. `boot(image, version)` may run once per reset epoch. It never enables actuation by itself. `process(command, tag, temperature, timestamp)` evaluates a single atomic transaction, returns a `Decision`, and appends a packed event after boot completion. Pre-boot commands are denied and cannot start a trusted audit epoch. Both ALLOW and BLOCK after completed boot are recorded.

Command payload bytes are `>BHI` (u8 ID, u16 value, u32 sequence). The tag authenticates **all** payload bytes. Sequence state starts at zero, so the first accepted sequence is at least one. A valid fresh sequence is consumed before policy evaluation, even for a policy-denied action. Failed authentication does not advance sequence. Unknown IDs are denied. Counter exhaustion disables output and raises an explicit error rather than silently wrapping or accepting an unlogged decision.

An event is `>IIBHHBH`: counter:u32, timestamp_low:u32, command_id:u8, value:u16, sensor/temperature:u16, decision+reason:u8, version:u16. Its 16 bytes follow the proposal's example layout. Reason values and big-endian encoding are software conventions. The model's genesis hashes a domain label, device ID, measured image digest, supplied version and boot outcome. The hardware genesis protocol is still pending.

`checkpoint()` returns device ID, event counter and current head. `verify_log(records, genesis, device_id, checkpoint)` recomputes each record, validates counter ordering, and compares the chain prefix at the retained checkpoint. A valid extension beyond that checkpoint is accepted. A shorter chain or wrong anchored head/device is rejected. `verify_stored_log` compares against the model's own retained head and latches `tamper_flag` on rejection. A caller must obtain genesis/checkpoint from a trusted source, not from the same potentially modified log file.

`reset()` disables actuation and clears runtime trust, sequence, event counter and in-memory log, preserving immutable fixture configuration. It does not create persistent anti-replay state, simulate a hardware reset mid-cycle or erase secrets securely from Python memory. Save checkpoints independently before reset if testing historical logs. Repeat boots can reproduce genesis; cross-reset epoch freshness remains unresolved.

The model has an unbounded event list, supplied timestamp and atomic calls. It does not model SHA scheduling, BRAM overflow, PWM duration, actual actuator completion, configuration-register locks, asynchronous clocks, production provisioning or backend networking. See [source notes](../docs/source-notes.md) for open assumptions and [verification plan](../docs/verification-plan.md) for hardware work still required.
