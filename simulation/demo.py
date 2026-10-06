"""Run: python -m simulation.demo. Public demo fixtures, software only."""

from dataclasses import replace
import hashlib

from .reference_model import Command, Configuration, SafeTraceModel, sign_command


def main() -> None:
    image = b'SafeTrace Lite public test application v2'
    public_fixture_key = bytes(range(32))
    model = SafeTraceModel(Configuration(hashlib.sha256(image).digest(), public_fixture_key, 2))
    print('SOFTWARE FUNCTIONAL DEMO - no FPGA/RTL or timing result')
    print('Valid boot:', model.boot(image, 2).reason.name,
          '| actuator enabled:', model.actuator_enable)
    for label, command in [('safe', Command(1, 60, 1)),
                           ('unsafe', Command(1, 100, 2)),
                           ('replay', Command(1, 60, 1))]:
        decision = model.process(command, sign_command(public_fixture_key, command), 40)
        print(f'{label}: {"ALLOW" if decision.allow else "BLOCK"} ({decision.reason.name})')
    print('Clean anchored log:', model.verify_stored_log(model.records))
    copied = list(model.records)
    altered = bytearray(copied[0].event)
    altered[13] ^= 0x80  # Decision bit in the fixed event layout.
    copied[0] = replace(copied[0], event=bytes(altered))
    print('Modified stored log:', model.verify_stored_log(copied))
    print('Tamper flag:', model.tamper_flag, '| event counter:', model.event_counter)


if __name__ == '__main__':
    main()
