# Proposal Traceability and Open Decisions

The conceptual source is *SafeTrace_Lite_PERURI_Proposal_DOI_Revisi (1).pdf*, 11 pages, supplied by the project owner. It is intentionally not committed: repository content does not need team/contact placeholders or the original attachment. Publication metadata verification supplements the bibliography only; it does not replace the proposal as the design authority.

Source PDF SHA-256: `a3109a4277d083e495f03d3f41c476e26162a627e7c02eaddd0fc3f1660fa12f`. This identifies the reviewed revision without publishing the attachment.

## Source mapping

| Proposal location | Repository coverage |
| --- | --- |
| pp. 1-2, Executive Summary | README overview/solution, architecture lifecycle and hardware split |
| pp. 2-3, Problem Statement | README problem, research motivation and novelty boundary |
| pp. 3-4, Threat Model and MVP | README limitations, architecture security boundary |
| p. 4, Figures 1-2 | Mermaid/PNG: HPS transport, trusted sensor proxy, FPGA checks, actuation, audit/checkpoint |
| pp. 4-5, Principles and RTL modules | Architecture module specifications and workflows |
| pp. 5-6, Event format, equations, memory | Architecture cryptography/memory; model event packing |
| p. 6, Interfaces/security/area | Architecture host lock/default-deny/shared core |
| pp. 7-9, Budgets and section 3.2 | README targets, verification T1-T12 and measurement requirements |
| pp. 9-10, References [1]-[16] | DOI bibliography, with metadata corrections recorded there |
| pp. 10-11, Bootcamp and future work | README roadmap and simulation integration plan |

## Clarifications without changing the concept

The example event fields total 128 bits. Previous hash (256) + event (128) = 384 message bits before SHA padding, not a 384-bit event plus previous hash. The one-block conclusion in the proposal remains valid.

An audit event records the gate decision, not actuator completion or a physically authenticated timestamp. `timestamp_low` is a supplied demo field, not a secure clock. HMAC authenticates commands, not the independently sampled sensor state.

## Model conventions, not finalized hardware requirements

| Decision | Software convention / outstanding RTL work |
| --- | --- |
| Command encoding | Big-endian `command_id:u8`, `value:u16`, `sequence:u32`; all seven bytes enter HMAC. Only command ID 1 (speed percentage) is supported in this model. Proposal does not fix these widths/encoding. |
| Event encoding | The proposal's 128-bit example, big-endian. Decision/reason byte uses bit 7 for ALLOW and low 7 bits for a model reason enumeration. |
| Policy | Speed <=80%, temperature <=70 in example fixtures. Speed limit 80 comes from proposal; temperature 70 is a test fixture, not a required physical threshold. |
| Sequence commit | A fresh authenticated command consumes its sequence before policy evaluation, even if policy denies it. Invalid HMAC does not advance state. Width/commit semantics still need approval within RTL design. |
| Genesis | Model hashes a domain label, device ID, measured image digest, supplied version and boot reason. This deterministically binds the boot outcome for software tests; exact hardware genesis/session format is pending. |
| Boot lifecycle | One boot verification per model reset epoch. Commands before completed boot are rejected; demo assumes runtime begins after that verification. |
| Reset | Runtime trust/sequence/counter/log state is cleared and outputs disabled; immutable demo configuration remains. Separate session identity and persistent anti-replay/anti-rollback are future decisions. Repeated identical boots yield identical model genesis. |
| Checkpoint | In-memory immutable snapshot retained independently in a test variable. Verifier accepts a log extending that checkpoint and rejects missing or mismatched anchored prefixes. No network/backend is implemented. |
| Buffer / transactions | Model stores an unbounded Python list and evaluates commands atomically. It does not model BRAM depth, overflow, scheduler cycles, mid-transaction reset, GPIO/PWM timing, or host-register locks. |

## Issues to settle before RTL integration

1. Bind image security-version metadata to a trusted image manifest/digest. The proposal compares a supplied version; HPS-supplied metadata alone is not proof of the image's true version.
2. Define replay/counter/session persistence across reset and reconfiguration, counter rollover, and backend epoch selection. The prototype establishes within-session monotonicity only.
3. Define key/digest/policy provisioning, configuration-lock/reset behavior and protection from host reads/writes.
4. Define scheduler fairness, SHA state ownership, transaction capture/backpressure, event-buffer overflow, and whether log failure must inhibit actuation. Silent evidence loss must not be presented as complete logging.
5. Define genesis bytes, checkpoint authenticity/retention and coherent counter/head readout. A hostile transport must not be able to create a falsely trusted anchor.
6. Define reset precedence and completion semantics for pending authentication/output/log operations, actuator signal duration, sensor snapshot timing and malformed-command handling.

These are specification gaps and proposed follow-up decisions, not claims that additional production security has already been implemented.
