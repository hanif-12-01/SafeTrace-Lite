# SafeTrace Lite

**Lightweight FPGA Lifecycle Security Core for Industrial Cyber-Physical Systems**

**"Trust what runs. Trust what acts. Trust what happened."**

## Project Overview

SafeTrace Lite proposes a small FPGA security IP core connecting application-image integrity, authenticated safe actuation, and verifiable decision history. The design targets the **DE10-Nano / Cyclone V FPGA** for PERURI Chip Hackathon 2026. A single shared SHA-256 hardware core serves all three security layers.

The source of truth is the supplied *SafeTrace Lite PERURI Proposal DOI Revisi*, an 11-page proposal. This repository translates that design into specifications and a software functional reference model. [Source mapping and open design decisions](docs/source-notes.md) distinguish proposal requirements from model conventions.

## Problem Statement

Industrial cyber-physical systems connect software and networks to sensors, actuators, and physical processes. A modified application image, a forged or replayed command, or an authentic command that violates a physical limit can affect the process. Editable logs can also weaken incident evidence. SafeTrace Lite proposes a hardware checkpoint joining the image that is accepted, the action that is allowed, and the decision that is recorded. Its contribution is this integration and resource sharing, rather than a new cryptographic primitive or a claim of being the first such system.

## Proposed Solution

The HPS ARM hosts the UI and transports test images, commands, and logs. FPGA fabric performs the security decisions. Startup verification establishes `SYSTEM_TRUSTED`; each subsequent command must pass authentication, freshness, and a deterministic safety policy. Every ALLOW/BLOCK decision becomes an audit event. A backend retains counter/hash checkpoints to help detect inconsistent or truncated histories.

## Three Security Layers

| Layer | Checks / output | MVP boundary |
| --- | --- | --- |
| **Boot Integrity Gate** | SHA-256 image digest matches a trusted reference; security version meets the configured minimum | Verifies a test application image before `ACTUATOR_ENABLE`. It does not replace the board's native secure boot or provide production firmware signature verification. |
| **Runtime Action Guard** | HMAC-SHA256, increasing sequence number, hardware safety policy; final ALLOW/BLOCK | An authenticated command still needs a safe value and sensor context. |
| **TrustLog** | Event counter, SHA-256 hash chain, chain-head checkpoint | Tamper evidence through verification. Data can still be modified; unanchored tail deletion is not intrinsically detectable. |

$$
\mathrm{ALLOW} = \mathrm{SYSTEM\_TRUSTED} \land \mathrm{HMAC\_VALID} \land \mathrm{FRESH\_SEQUENCE} \land \mathrm{POLICY\_VALID}
$$

## System Architecture Diagram

![SafeTrace Lite proposed hardware architecture](docs/block-diagram.png)

Solid arrows carry data, configuration, or decisions. Dashed arrows identify SHA service requests/results. BLOCK leaves the output disabled; both decisions feed TrustLog. The FPGA boundary contains all decision logic. The figure is a design specification, not a hardware test result. [Editable Mermaid source](docs/block-diagram.mmd), [architecture details](docs/architecture.md), and [local PNG renderer](tools/render_diagram.py) are included.

## Hardware Target & Technology

Planned target: DE10-Nano, Cyclone V SE **5CSEBA6U23I7**, HPS ARM, Avalon-MM through the lightweight HPS-to-FPGA bridge, Platform Designer, and Verilog/SystemVerilog. Demo sensor inputs use switches/ADC/GPIO; demo outputs use LED/PWM or a low-voltage motor through a driver.

The following are **engineering target — not measured result**, from proposal pp. 7-9:

| Metric | Initial target |
| --- | --- |
| FPGA clock | 50 MHz, subject to Quartus timing analysis |
| Logic / registers | <=4,000 ALMs / <=5,000 FFs |
| BRAM / DSP | <=128 Kbit / 0 DSP blocks |
| SHA-256 block latency | <5 microseconds at 50 MHz |
| Short-command HMAC latency | <25 microseconds at 50 MHz |
| Policy evaluation | <=5 cycles after authentication/sequence checks |
| TrustLog update | One SHA block for a 128-bit event plus 256-bit previous hash, plus control |

No RTL, synthesis, timing, power, or on-board result is available. Shared-core contention must be included in future end-to-end latency measurements.

## Security-by-Design

The proposed output gate defaults to BLOCK during reset, untrusted boot, or error. Trusted digest, HMAC key, minimum version, and policy configuration belong to the FPGA trust boundary; host writes must be denied after configuration lock. The key remains protected from host readout. Sequence validation precedes policy execution. ALLOW and BLOCK are both logged. Hash chaining provides integrity evidence, not encryption or confidentiality.

## Threat Model & Limitations

The MVP addresses modified test images, images below the minimum security version, invalid HMACs, replay within the current session, unsafe commands or sensor context, log modification, and checkpoint-visible tail truncation.

It excludes invasive physical attacks, side channels, fault injection/key extraction, spoofing before the trusted sensor interface, network availability/DoS, full backend security, and production key provisioning. Backend anchors are assumed to be retained independently and trusted. Reset-safe persistence, authenticated image-version binding, checkpoint ingestion, and buffer-overflow behavior still need explicit RTL/protocol decisions; see [source notes](docs/source-notes.md). A linear unkeyed hash chain alone does not prevent complete history rewriting by an attacker who can also replace its trusted anchor.

## Project Structure

```text
SafeTrace-Lite/
├── README.md
├── .gitignore
├── docs/
│   ├── architecture.md
│   ├── block-diagram.mmd
│   ├── block-diagram.png
│   ├── verification-plan.md
│   ├── references.md
│   └── source-notes.md
├── simulation/
│   ├── README.md
│   ├── __init__.py
│   ├── reference_model.py
│   └── demo.py
├── tests/
│   ├── README.md
│   └── test_reference_model.py
└── tools/
    ├── render_diagram.py
    └── validate_repository.py
```

## Verification Strategy

[The verification plan](docs/verification-plan.md) maps proposal section 3.2 to T1-T12. Run the functional model tests with Python 3.10+ and the standard library:

```sh
python -m unittest discover -s tests -v
python -m simulation.demo
python tools/validate_repository.py
```

The model checks functional decisions and audit verification only. Planned Verilator/ModelSim plus cocotb work must separately verify RTL interfaces, SHA/HMAC known-answer vectors, scheduler ownership, cycle timing, and reset during transactions. Quartus and SignalTap will provide synthesis, timing, and physical-output evidence later. [Simulation roadmap](simulation/README.md) and [test coverage limits](tests/README.md) describe the distinction.

## Development Roadmap

| Stage | Deliverables | Status |
| --- | --- | --- |
| Repository preparation | Architecture, diagram, verification specification, DOI bibliography | Included |
| Functional reference | Python boot/HMAC/replay/policy/hash chain/checkpoint model | Included; software only |
| Bootcamp day 1 | SHA integration, register interface, Boot Integrity Gate, SHA vectors, Action Guard skeleton | Planned |
| Bootcamp day 2 | HMAC/replay/policy, fixed events, TrustLog, end-to-end RTL tests, Quartus report | Planned |
| Bootcamp day 3 | HPS bridge, SignalTap, LED/PWM/motor demo, attack presets, video and measured metrics | Planned |
| Future work | PUF/secure provisioning, ECC firmware signatures, provisionable locked policy tables, broader sensors and fault testing, optional ASIC exploration, Merkle/history trees | Outside MVP |

The three-day bootcamp schedule is the proposal's plan, not evidence of completed work. Optional Yosys/OpenROAD with SkyWater 130 nm is an exploratory future path.

## Research References

[The DOI bibliography](docs/references.md) retains proposal references [1]-[16]: ICPS security [1]-[4], secure bootstrap/root of trust [5]-[6], runtime assurance and lightweight trusted hardware [7]-[8], secure logging [9]-[10], HMAC [11], FPGA SHA-256 [12]-[13], and DOI-bearing NIST technical standards [14]-[16]. Board/competition documents are identified separately as specifications and requirements.

## Project Status

**Proposed Architecture / Pre-Implementation**

Documentation and a software functional reference model are present. FPGA RTL, cocotb integration, Quartus projects/bitstreams, synthesis, hardware tests, and benchmarks remain planned. Python test results cannot establish FPGA correctness, timing, resource use, or resistance to physical attacks.
