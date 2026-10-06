# Verification Plan

Status: **planned hardware verification**. Primary source: proposal section **3.2 Rencana Pengujian**, pp. 7-9. The Python reference exercises functional expectations; it does not implement RTL, timing, buses, or physical outputs. Proposed signal names describe future observations, not signals already present in a bitstream.

## T1-T12 acceptance scenarios

Unless stated otherwise, configure trusted image digest, a prototype key, minimum version, speed limit 80%, and a safe sensor threshold before locking configuration. Runtime tests start with a successful boot. Model fixtures use temperature threshold 70 as a software example. Check decisions, state changes and event records together, not just a return value.

### T1 — Valid startup image

| Field | Plan |
| --- | --- |
| Objective | Establish runtime trust only for an accepted image/version. |
| Preconditions | Reset gives BLOCK; trusted reference and minimum version configured/locked. |
| Input stimulus | Stream complete image with matching digest and version >=minimum. |
| Expected behavior | Digest/version checks pass; runtime gate becomes eligible, but boot alone does not authorize a command. |
| Expected output signals | `SYSTEM_TRUSTED=1`, boot complete; `ACTUATOR_ENABLE=0` until a valid runtime decision. |
| Pass/fail criteria | Trust asserted only after complete successful verification; no actuator enable during hashing. |
| Planned verification method | Python digest/version check; cocotb full image streaming against reference; waveform checks for enable timing. |

### T2 — Modified firmware image

| Field | Plan |
| --- | --- |
| Objective | Reject modified image bytes. |
| Preconditions | Digest provisioned for original image; output initially BLOCK. |
| Input stimulus | Flip one bit in the streamed image; keep admissible version. |
| Expected behavior | Digest mismatch prevents runtime trust; attempted commands stay BLOCK. |
| Expected output signals | `SYSTEM_TRUSTED=0`, digest mismatch status, `ACTUATOR_ENABLE=0`, BLOCK. |
| Pass/fail criteria | Any mismatched complete image remains untrusted; failed boot cannot reuse previous valid state. |
| Planned verification method | Python bit-flip case; RTL stream test with independent digest and output assertions; board LED/status demo. |

### T3 — Firmware rollback

| Field | Plan |
| --- | --- |
| Objective | Enforce the configured minimum version. |
| Preconditions | Matching trusted image digest, protected minimum version. |
| Input stimulus | Matching digest but supplied version <minimum. |
| Expected behavior | Version gate rejects image despite digest success. |
| Expected output signals | `ROLLBACK=1`, `SYSTEM_TRUSTED=0`, BLOCK, `ACTUATOR_ENABLE=0`. |
| Pass/fail criteria | Lower version always denied; version equality accepted in T1 variant. This tests comparison, not authenticated version metadata. |
| Planned verification method | Python version cases; RTL version-comparator boundaries and locked-register checks; future signed-manifest binding separately. |

### T4 — Valid authenticated command

| Field | Plan |
| --- | --- |
| Objective | Permit an authenticated, fresh, safe action and record evidence. |
| Preconditions | Trusted boot, last sequence lower than input, safe temperature. |
| Input stimulus | Valid HMAC over complete command payload; fresh sequence; speed=60 with max=80. |
| Expected behavior | HMAC, freshness and policy pass; sequence advances; ALLOW event committed to TrustLog. |
| Expected output signals | `HMAC_VALID=1`, `FRESH_SEQUENCE=1`, `POLICY_VALID=1`, ALLOW, `ACTUATOR_ENABLE=1`; event-valid, increased counter/new chain head after log completion. |
| Pass/fail criteria | Correct command reaches gated output, exactly one committed decision event, independently recomputed hash matches. |
| Planned verification method | Python decision/chain checks; cocotb end-to-end transaction; SignalTap and LED/PWM/low-voltage-driver observation. |

### T5 — Forged command

| Field | Plan |
| --- | --- |
| Objective | Reject an incorrect HMAC without poisoning replay state. |
| Preconditions | Trusted boot and known last sequence. |
| Input stimulus | Incorrect tag, or alter authenticated command ID/value/sequence after signing. |
| Expected behavior | BLOCK with AUTH_FAIL; event recorded; last sequence unchanged. |
| Expected output signals | `HMAC_VALID=0`, BLOCK, `reason_code=AUTH_FAIL`, `ACTUATOR_ENABLE=0`; event/counter/head update. |
| Pass/fail criteria | No output activation, no unauthorized sequence update; payload/tag modifications detected. |
| Planned verification method | Python bad-tag/all-field tests; cocotb independent HMAC vectors and malformed-length cases; board attack preset. |

### T6 — Replay attack

| Field | Plan |
| --- | --- |
| Objective | Reject repeated or older authenticated sequences. |
| Preconditions | An authenticated fresh command has established `last_sequence`. |
| Input stimulus | Valid HMAC with sequence ==last or <last. |
| Expected behavior | BLOCK with REPLAY; last sequence does not decrease; deny event recorded. |
| Expected output signals | `HMAC_VALID=1`, `FRESH_SEQUENCE=0`, BLOCK, `reason_code=REPLAY`, `ACTUATOR_ENABLE=0`. |
| Pass/fail criteria | Equal/older values denied; fresh value accepted if policy safe; unauthenticated high sequence cannot poison state. |
| Planned verification method | Python equality/older tests; RTL update timing, max-value/no-wrap tests and sequence-state readout. Cross-reset freshness needs a separate session/persistence design. |

### T7 — Safety boundary pass

| Field | Plan |
| --- | --- |
| Objective | Confirm inclusive safety limit. |
| Preconditions | Trusted boot, valid HMAC/fresh sequence, safe sensor context, max speed=80. |
| Input stimulus | speed=80. Include sensor temperature exactly equal to its threshold as a variant. |
| Expected behavior | Boundary equality passes; ALLOW event recorded. |
| Expected output signals | `POLICY_VALID=1`, ALLOW, `ACTUATOR_ENABLE=1`. |
| Pass/fail criteria | Exact configured limit is allowed and output value remains the authenticated requested value. |
| Planned verification method | Python boundary equality; cocotb comparators and output value; SignalTap policy result. |

### T8 — Safety boundary fail

| Field | Plan |
| --- | --- |
| Objective | Reject a value immediately above the limit even when authentic. |
| Preconditions | Trusted boot, valid HMAC/fresh sequence, safe sensor, max speed=80. |
| Input stimulus | speed=81; board demo may also use speed=100. |
| Expected behavior | BLOCK with POLICY; event recorded. Sequence update follows finalized commit semantics (model consumes fresh authenticated sequence). |
| Expected output signals | `HMAC_VALID=1`, `FRESH_SEQUENCE=1`, `POLICY_VALID=0`, BLOCK, `reason_code=POLICY`, `ACTUATOR_ENABLE=0`. |
| Pass/fail criteria | No actuation for 81 or higher; correct denial reason and audit entry. |
| Planned verification method | Python one-over case; RTL comparator boundaries, event checking and output assertions; board unsafe-command demo. |

### T9 — Unsafe sensor context

| Field | Plan |
| --- | --- |
| Objective | Deny otherwise safe authentic command under unsafe physical context. |
| Preconditions | Trusted boot, valid tag/fresh sequence, value within limit. |
| Input stimulus | Trusted proxy temperature >configured threshold. |
| Expected behavior | BLOCK with POLICY based on sensor snapshot; record that snapshot. |
| Expected output signals | `POLICY_VALID=0`, BLOCK, `reason_code=POLICY`, `ACTUATOR_ENABLE=0`. |
| Pass/fail criteria | Unsafe context denies command; event sensor field equals the sample used for decision. |
| Planned verification method | Python threshold fixture; cocotb sensor equality/one-over and snapshot consistency; board switch/ADC/GPIO proxy. Spoofing before interface remains excluded. |

### T10 — Log modification

| Field | Plan |
| --- | --- |
| Objective | Detect changed stored evidence during verification. |
| Preconditions | Generated events/hashes and independently retained genesis/checkpoint. |
| Input stimulus | Flip a stored event bit (including decision field); also try recomputing stored hashes while keeping trusted checkpoint unchanged. |
| Expected behavior | Recomputed digest or anchored head mismatch; verification rejects history. |
| Expected output signals | Verify failure / `tamper_flag=1`; no actuation is implied by audit verification. |
| Pass/fail criteria | Changed record rejected against trusted material; clean chain passes. Tamper flag behavior/reset must match finalized controller specification. |
| Planned verification method | Python log-copy bit flip and recomputed-chain case; RTL verify-mode tests; board log-copy demo. |

### T11 — Log tail truncation

| Field | Plan |
| --- | --- |
| Objective | Detect history older than an independently retained checkpoint. |
| Preconditions | Backend/test fixture retains `{device_id, counter=105, chain_head_at_105}`. |
| Input stimulus | Present storage ending at counter=104, with otherwise internally valid prefix hashes. |
| Expected behavior | Checkpoint count exceeds available history; truncation/checkpoint mismatch reported. |
| Expected output signals | Backend verify/checkpoint mismatch or truncation alert. A hardware `tamper_flag` requires explicit backend-to-FPGA reporting and is not assumed. |
| Pass/fail criteria | Anchored truncation rejected; intact 105-record chain and valid extensions pass. Do not claim detection of every unanchored tail deletion. |
| Planned verification method | Python 105→104 example, forged head/wrong-device/extension variants; planned HPS/backend integration and coherent checkpoint export test. |

### T12 — Reset behavior

| Field | Plan |
| --- | --- |
| Objective | Restore safe default state and prevent stale ALLOW across reset. |
| Preconditions | Exercise idle, trusted runtime, active SHA/HMAC, pending output and pending log commit. |
| Input stimulus | Assert reset at each RTL transaction phase, including immediately before decision-valid. |
| Expected behavior | Output becomes BLOCK; trust/valid flags and scheduler ownership clear; incomplete operations cannot resurrect an old decision. Reset persistence/lock/session handling must be specified separately. |
| Expected output signals | `ACTUATOR_ENABLE=0`, `SYSTEM_TRUSTED=0`, no stale ALLOW/digest/event valid; safe reset status. |
| Pass/fail criteria | No active output during/after reset until new boot and authenticated safe command; defined behavior for partial event updates. |
| Planned verification method | Python reset between atomic calls checks safe state only. Mid-transaction reset, asynchronous reset timing and bus/clock-domain effects require cocotb/RTL and SignalTap; they remain untested. |

## Tools and verification stages

| Stage / tools | Required evidence before claiming completion |
| --- | --- |
| Python standard-library reference | Real unittest output for decisions, serialization and anchor verification; no timing/resource inference. |
| Verilator / ModelSim | Compile actual RTL; unit and integration simulations with meaningful waveform/assertion evidence. |
| cocotb + Python | Drive actual module ports, compare digest/tag/decision/event bytes with independent reference, verify handshakes and reset phases. |
| Intel Quartus Prime + Platform Designer | Build for Cyclone V SE 5CSEBA6U23I7; synthesis/fitter utilization, register map, timing constraints, 50 MHz timing report and Power Analyzer if power is reported. |
| SignalTap Logic Analyzer | Capture FSMs, SHA request/valid/owner, sequence checks, policy result, output gate, event counter, chain head/tamper status on the board. |
| Physical demo | Valid/modified/rollback startup; safe/unsafe/replayed command; modified log and anchored truncation; LED/PWM or low-voltage motor via driver. |

Before end-to-end RTL tests, run SHA/HMAC known-answer vectors independent of the hardware implementation. Exercise SHA padding at 55/56/63/64-byte message sizes and multi-block image inputs. Test scheduler ownership under contention, configuration lock/read protection, malformed traffic, BRAM backpressure and counter overflow. Tests must enforce transaction identity so validity flags from separate commands cannot combine into ALLOW.

## Engineering targets and honest reporting

All numbers here are **engineering target — not measured result**: 50 MHz; <=4,000 ALM; <=5,000 FF; <=128 Kbit BRAM; 0 DSP; one SHA block <5 microseconds; short HMAC <25 microseconds; policy <=5 cycles after auth/sequence; log one block plus control. Shared scheduler wait and host transfers must be accounted for separately in measured end-to-end latency.

Success targets are: every defined SHA/HMAC known-answer vector passes; T2/T3/T5/T6/T8/T9 produce BLOCK; T10/T11 produce correct audit alerts; reset/untrusted/error states keep output inactive; event counters/heads are consistent. The proposed end-to-end demo lasts 3-5 minutes. None of these FPGA targets has been measured in this repository.

Future reports must record commit, tool versions, exact device/clock constraints, vector set, passing/failing scenarios, observed cycles, utilization and limitations. Do not fabricate waveforms, board photographs, benchmarks, or synthesis results. [Software coverage](../tests/README.md) records what can be checked now.
