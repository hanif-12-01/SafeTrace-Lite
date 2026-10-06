"""Jalankan: python -m simulation.demo. Data demo publik, perangkat lunak saja."""

from dataclasses import replace
import hashlib

from .reference_model import Command, Configuration, SafeTraceModel, sign_command


def main() -> None:
    image = b'SafeTrace Lite public test application v2'
    public_fixture_key = bytes(range(32))
    model = SafeTraceModel(Configuration(hashlib.sha256(image).digest(), public_fixture_key, 2))
    print('DEMO FUNGSIONAL PERANGKAT LUNAK - FPGA/RTL dan timing belum diuji')
    print('Boot valid:', model.boot(image, 2).reason.name,
          '| aktuator aktif:', model.actuator_enable)
    for label, command in [('aman', Command(1, 60, 1)),
                           ('tidak aman', Command(1, 100, 2)),
                           ('pengulangan', Command(1, 60, 1))]:
        decision = model.process(command, sign_command(public_fixture_key, command), 40)
        print(f'{label}: {"ALLOW" if decision.allow else "BLOCK"} ({decision.reason.name})')
    clean = model.verify_stored_log(model.records)
    print('Log bersih dengan checkpoint:', 'VALID' if clean.valid else 'TIDAK VALID', f'({clean.reason})')
    copied = list(model.records)
    altered = bytearray(copied[0].event)
    altered[13] ^= 0x80  # Bit keputusan pada format peristiwa tetap.
    copied[0] = replace(copied[0], event=bytes(altered))
    modified = model.verify_stored_log(copied)
    print('Log tersimpan yang diubah:', 'VALID' if modified.valid else 'TIDAK VALID', f'({modified.reason})')
    print('Indikator perubahan:', model.tamper_flag, '| penghitung peristiwa:', model.event_counter)


if __name__ == '__main__':
    main()
