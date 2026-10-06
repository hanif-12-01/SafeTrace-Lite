"""Uji fungsional; reset di tengah transaksi RTL masih merupakan rencana lanjutan."""

from dataclasses import replace
import hashlib
import hmac
import struct
import unittest

from simulation.reference_model import (
    Checkpoint, Command, Configuration, EVENT_FORMAT, LogRecord, MAX_COUNTER,
    Reason, SafeTraceModel, sign_command, verify_log,
)


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        self.image = b'SafeTrace Lite public test image v2'
        self.key = bytes(range(32))  # Data uji perangkat lunak yang memang bersifat publik.
        self.model = SafeTraceModel(Configuration(hashlib.sha256(self.image).digest(), self.key, 2))

    def boot(self):
        return self.model.boot(self.image, 2)

    def send(self, value=60, sequence=1, temperature=40, command_id=1):
        command = Command(command_id, value, sequence)
        return self.model.process(command, sign_command(self.key, command), temperature, 123)

    def test_t1_valid_startup_image(self):
        self.assertTrue(self.boot().allow)
        self.assertTrue(self.model.system_trusted)
        self.assertFalse(self.model.actuator_enable)

    def test_t2_modified_image(self):
        changed = bytes([self.image[0] ^ 1]) + self.image[1:]
        self.assertEqual(self.model.boot(changed, 2).reason, Reason.DIGEST_MISMATCH)
        self.assertFalse(self.model.system_trusted)
        self.assertEqual(self.send().reason, Reason.UNTRUSTED)
        self.assertFalse(self.model.actuator_enable)

    def test_t3_rollback(self):
        self.assertEqual(self.model.boot(self.image, 1).reason, Reason.ROLLBACK)
        self.assertFalse(self.model.system_trusted)
        self.assertFalse(self.model.actuator_enable)

    def test_t4_valid_authenticated_command_and_event(self):
        self.boot()
        result = self.send()
        self.assertTrue(result.allow)
        self.assertTrue(self.model.actuator_enable)
        self.assertEqual(self.model.last_sequence, 1)
        expected = struct.pack('>IIBHHBH', 1, 123, 1, 60, 40, 128, 2)
        self.assertEqual(self.model.records[0].event, expected)
        self.assertEqual(self.model.chain_head, hashlib.sha256(self.model.genesis + expected).digest())

    def test_t5_forged_command_does_not_advance_sequence(self):
        self.boot()
        command = Command(1, 60, 99)
        self.assertEqual(self.model.process(command, bytes(32), 40).reason, Reason.AUTH_FAIL)
        self.assertEqual(self.model.last_sequence, 0)
        self.assertFalse(self.model.actuator_enable)
        self.assertEqual(self.model.event_counter, 1)
        self.assertTrue(self.send(sequence=1).allow)

    def test_t6_equal_and_older_replay(self):
        self.boot()
        self.assertTrue(self.send(sequence=2).allow)
        for sequence in (2, 1):
            self.assertEqual(self.send(sequence=sequence).reason, Reason.REPLAY)
            self.assertEqual(self.model.last_sequence, 2)
            self.assertFalse(self.model.actuator_enable)
        self.assertEqual(self.model.event_counter, 3)

    def test_t7_boundary_pass(self):
        self.boot()
        self.assertTrue(self.send(value=80, temperature=70).allow)

    def test_t8_boundary_fail(self):
        self.boot()
        self.assertEqual(self.send(value=81).reason, Reason.POLICY)
        self.assertFalse(self.model.actuator_enable)
        self.assertEqual(self.model.last_sequence, 1)

    def test_t9_unsafe_sensor(self):
        self.boot()
        self.assertEqual(self.send(temperature=71).reason, Reason.POLICY)
        self.assertFalse(self.model.actuator_enable)
        self.assertEqual(EVENT_FORMAT.unpack(self.model.records[0].event)[4], 71)

    def test_t10_log_modification(self):
        self.boot()
        self.send()
        changed = bytearray(self.model.records[0].event)
        changed[13] ^= 128
        bad = [replace(self.model.records[0], event=bytes(changed))]
        self.assertFalse(self.model.verify_stored_log(bad).valid)
        self.assertTrue(self.model.tamper_flag)

    def test_t11_tail_truncation_105_to_104(self):
        self.boot()
        for sequence in range(1, 106):
            self.send(sequence=sequence)
        checkpoint = self.model.checkpoint()
        self.assertEqual(checkpoint.counter, 105)
        result = verify_log(self.model.records[:-1], self.model.genesis, self.model.device_id, checkpoint)
        self.assertFalse(result.valid)
        self.assertEqual(result.reason, 'TRUNCATION')
        self.assertTrue(verify_log(self.model.records, self.model.genesis, self.model.device_id, checkpoint).valid)

    def test_t12_reset_safe_state_between_atomic_calls(self):
        self.boot()
        self.send()
        self.model.reset()
        self.assertFalse(self.model.system_trusted)
        self.assertFalse(self.model.actuator_enable)
        self.assertEqual(self.model.last_sequence, 0)
        self.assertEqual(self.model.event_counter, 0)
        self.assertEqual(self.model.records, [])
        self.assertEqual(self.send().reason, Reason.UNTRUSTED)
        self.assertTrue(self.boot().allow)
        self.assertFalse(self.model.actuator_enable)

    def test_default_deny_before_boot(self):
        self.assertEqual(self.send().reason, Reason.UNTRUSTED)
        self.assertFalse(self.model.actuator_enable)
        self.assertEqual(self.model.records, [])

    def test_unknown_command(self):
        self.boot()
        self.assertEqual(self.send(command_id=255).reason, Reason.POLICY)

    def test_all_command_fields_are_authenticated(self):
        original = Command(1, 60, 1)
        tag = sign_command(self.key, original)
        for changed in (replace(original, command_id=2), replace(original, value=61),
                        replace(original, sequence=2)):
            model = SafeTraceModel(self.model.config)
            model.boot(self.image, 2)
            self.assertEqual(model.process(changed, tag, 40).reason, Reason.AUTH_FAIL)

    def test_policy_denial_consumes_fresh_authenticated_sequence(self):
        self.boot()
        self.assertEqual(self.send(value=81, sequence=3).reason, Reason.POLICY)
        self.assertEqual(self.send(value=60, sequence=3).reason, Reason.REPLAY)

    def test_valid_extension_beyond_checkpoint(self):
        self.boot()
        self.send()
        checkpoint = self.model.checkpoint()
        self.send(sequence=2)
        self.assertTrue(verify_log(self.model.records, self.model.genesis, self.model.device_id, checkpoint).valid)

    def test_recomputed_history_cannot_replace_trusted_anchor(self):
        self.boot()
        self.send()
        checkpoint = self.model.checkpoint()
        changed = bytearray(self.model.records[0].event)
        changed[13] ^= 128
        forged = [LogRecord(bytes(changed), hashlib.sha256(self.model.genesis + changed).digest())]
        self.assertEqual(verify_log(forged, self.model.genesis, self.model.device_id, checkpoint).reason,
                         'CHECKPOINT_MISMATCH')

    def test_unanchored_tail_deletion_is_not_detectable(self):
        self.boot()
        self.send()
        self.send(sequence=2)
        self.assertTrue(verify_log(self.model.records[:-1], self.model.genesis, self.model.device_id).valid)

    def test_checkpoint_device_and_head_mismatch(self):
        self.boot()
        self.send()
        checkpoint = self.model.checkpoint()
        for bad in (replace(checkpoint, device_id='other-device'),
                    replace(checkpoint, chain_head=bytes(32))):
            self.assertFalse(verify_log(self.model.records, self.model.genesis, self.model.device_id, bad).valid)

    def test_empty_log_checkpoint_and_bad_genesis(self):
        self.boot()
        self.assertTrue(self.model.verify_stored_log([]).valid)
        bad = Checkpoint(self.model.device_id, 0, bytes(32))
        self.assertFalse(verify_log([], self.model.genesis, self.model.device_id, bad).valid)
        self.assertFalse(verify_log([], b'bad', self.model.device_id).valid)

    def test_reordered_and_malformed_records(self):
        self.boot()
        self.send()
        self.send(sequence=2)
        self.assertFalse(self.model.verify_stored_log(list(reversed(self.model.records))).valid)
        self.assertFalse(self.model.verify_stored_log([LogRecord(b'bad', bytes(32))]).valid)

    def test_maximum_sequence_does_not_wrap(self):
        self.boot()
        self.assertTrue(self.send(sequence=MAX_COUNTER).allow)
        self.assertEqual(self.send(sequence=0).reason, Reason.REPLAY)
        with self.assertRaises(ValueError):
            Command(1, 60, MAX_COUNTER + 1)

    def test_counter_exhaustion_prevents_unlogged_output(self):
        self.boot()
        self.send()
        self.model.event_counter = MAX_COUNTER  # Injeksi state batas untuk menguji kondisi maksimum.
        with self.assertRaises(OverflowError):
            self.send(sequence=2)
        self.assertFalse(self.model.actuator_enable)
        self.assertFalse(self.model.system_trusted)

    def test_malformed_input_disables_prior_output(self):
        self.boot()
        self.send()
        with self.assertRaises(ValueError):
            self.send(sequence=2, temperature=-1)
        self.assertFalse(self.model.actuator_enable)

    def test_boot_result_bound_to_genesis(self):
        self.boot()
        other = SafeTraceModel(self.model.config)
        other.boot(self.image, 1)
        self.assertNotEqual(self.model.genesis, other.genesis)

    def test_crypto_known_answers(self):
        self.assertEqual(hashlib.sha256(b'abc').hexdigest(),
                         'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
        self.assertEqual(hmac.new(bytes([0x0b]) * 20, b'Hi There', hashlib.sha256).hexdigest(),
                         'b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7')


if __name__ == '__main__':
    unittest.main()
