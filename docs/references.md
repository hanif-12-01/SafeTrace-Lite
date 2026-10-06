# Scientific References and DOI-Bearing Technical Standards

References [1]-[16] come from proposal section 4 (pp. 9-10). Numbering is preserved. Each entry has a DOI and a project relevance statement; relevance describes design motivation, not measured SafeTrace Lite performance.

Bibliographic metadata was checked against publisher-deposited [Crossref records](https://api.crossref.org/) for [1]-[13] and official NIST publication pages for [14]-[16] on **2026-10-06**. Minor author corrections are listed below. The proposal remains the architectural source of truth.

## Peer-reviewed scientific publications

### [1] Industrial cyber-physical security

- **Authors:** Hakan Kayan, Matthew Nunes, Omer Rana, Pete Burnap, Charith Perera.
- **Title:** Cybersecurity of Industrial Cyber-Physical Systems: A Review.
- **Publication / year:** *ACM Computing Surveys*, 54(11s), Article 229, 2022.
- **DOI:** [10.1145/3510410](https://doi.org/10.1145/3510410).
- **Relevance:** ICPS attack surfaces and the motivation for coordinated lifecycle security checks.

### [2] Cyber-physical security survey

- **Authors:** Abdulmalik Humayed, Jingqiang Lin, Fengjun Li, Bo Luo.
- **Title:** Cyber-Physical Systems Security-A Survey.
- **Publication / year:** *IEEE Internet of Things Journal*, 4(6), 1802-1831, 2017.
- **DOI:** [10.1109/JIOT.2017.2703172](https://doi.org/10.1109/JIOT.2017.2703172).
- **Relevance:** Links cyber compromise to sensing, control, and physical consequences.

### [3] Industrial networks

- **Authors:** Manuel Cheminod, Luca Durante, Adriano Valenzano.
- **Title:** Review of Security Issues in Industrial Networks.
- **Publication / year:** *IEEE Transactions on Industrial Informatics*, 9(1), 277-293, 2013.
- **DOI:** [10.1109/TII.2012.2198666](https://doi.org/10.1109/TII.2012.2198666).
- **Relevance:** Industrial constraints motivate a compact guard for critical physical commands.

### [4] Process-control attacks

- **Authors:** Alvaro A. Cardenas, Saurabh Amin, Zong-Syun Lin, Yu-Lun Huang, Chi-Yen Huang, Shankar Sastry.
- **Title:** Attacks against process control systems: risk assessment, detection, and response.
- **Publication / year:** *Proceedings of the 6th ACM Symposium on Information, Computer and Communications Security (ASIACCS)*, 355-366, 2011.
- **DOI:** [10.1145/1966913.1966959](https://doi.org/10.1145/1966913.1966959).
- **Relevance:** Supports evaluating physical context, beyond authenticating a network message.

### [5] Secure bootstrap

- **Authors:** W. A. Arbaugh, D. J. Farber, J. M. Smith.
- **Title:** A Secure and Reliable Bootstrap Architecture.
- **Publication / year:** *IEEE Symposium on Security and Privacy*, 65-71, 1997.
- **DOI:** [10.1109/SECPRI.1997.601317](https://doi.org/10.1109/SECPRI.1997.601317).
- **Relevance:** Chain-of-trust motivation for verifying an image before the next operational stage.

### [6] IoT boot and attestation

- **Authors:** Zhen Ling, Huaiyu Yan, Xinhui Shao, Junzhou Luo, Yiling Xu, Bryan Pearson, Xinwen Fu.
- **Title:** Secure boot, trusted boot and remote attestation for ARM TrustZone-based IoT Nodes.
- **Publication / year:** *Journal of Systems Architecture*, 119, 102240, 2021.
- **DOI:** [10.1016/j.sysarc.2021.102240](https://doi.org/10.1016/j.sysarc.2021.102240).
- **Relevance:** Boot measurement and integrity context; SafeTrace Lite's digest gate is a narrower prototype.

### [7] Runtime safety

- **Authors:** Stanley Bak, Deepti K. Chivukula, Olugbemiga Adekunle, Mu Sun, Marco Caccamo, Lui Sha.
- **Title:** The System-Level Simplex Architecture for Improved Real-Time Embedded System Safety.
- **Publication / year:** *15th IEEE Real-Time and Embedded Technology and Applications Symposium (RTAS)*, 99-107, 2009.
- **DOI:** [10.1109/RTAS.2009.20](https://doi.org/10.1109/RTAS.2009.20).
- **Relevance:** Motivation for separating small safety decision logic from complex controller software; no full Simplex controller is claimed here.

### [8] Lightweight trusted hardware

- **Authors:** Patrick Koeberl, Steffen Schulz, Ahmad-Reza Sadeghi, Vijay Varadharajan.
- **Title:** TrustLite: A Security Architecture for Tiny Embedded Devices.
- **Publication / year:** *Proceedings of the Ninth European Conference on Computer Systems (EuroSys)*, 2014.
- **DOI:** [10.1145/2592798.2592824](https://doi.org/10.1145/2592798.2592824).
- **Relevance:** Lightweight hardware trust-boundary motivation; SafeTrace Lite does not implement TrustLite's isolation architecture.

### [9] Secure audit logging

- **Authors:** Bruce Schneier, John Kelsey.
- **Title:** Secure Audit Logs to Support Computer Forensics.
- **Publication / year:** *ACM Transactions on Information and System Security*, 2(2), 159-176, 1999.
- **DOI:** [10.1145/317087.317089](https://doi.org/10.1145/317087.317089).
- **Relevance:** Integrity evidence for forensic histories; the MVP is a simpler hash chain and does not claim equivalent forward-security properties.

### [10] Secure logging and truncation

- **Authors:** Di Ma, Gene Tsudik.
- **Title:** A New Approach to Secure Logging.
- **Publication / year:** *ACM Transactions on Storage*, 5(1), Article 2, 2009.
- **DOI:** [10.1145/1502777.1502779](https://doi.org/10.1145/1502777.1502779).
- **Relevance:** Secure-history and tail-truncation motivation for retaining independent checkpoints.

### [11] HMAC construction

- **Authors:** Mihir Bellare, Ran Canetti, Hugo Krawczyk.
- **Title:** Keying Hash Functions for Message Authentication.
- **Publication / year:** *Advances in Cryptology-CRYPTO '96*, Lecture Notes in Computer Science, 1-15, 1996.
- **DOI:** [10.1007/3-540-68697-5_1](https://doi.org/10.1007/3-540-68697-5_1).
- **Relevance:** Keyed message authentication underlying HMAC-SHA256 command verification.

### [12] Compact FPGA SHA-256

- **Authors:** Rommel Garcia, Ignacio Algredo-Badillo, Miguel Morales-Sandoval, Claudia Feregrino-Uribe, Rene Cumplido.
- **Title:** A compact FPGA-based processor for the Secure Hash Algorithm SHA-256.
- **Publication / year:** *Computers & Electrical Engineering*, 40(1), 194-202, 2014.
- **DOI:** [10.1016/j.compeleceng.2013.11.014](https://doi.org/10.1016/j.compeleceng.2013.11.014).
- **Relevance:** Area/throughput tradeoffs and reuse motivate a shared engine; paper metrics are not SafeTrace Lite resource results.

### [13] SHA implementation tradeoffs

- **Authors:** Imtiaz Ahmad, A. Shoba Das.
- **Title:** Hardware implementation analysis of SHA-256 and SHA-512 algorithms on FPGAs.
- **Publication / year:** *Computers & Electrical Engineering*, 31(6), 345-360, 2005.
- **DOI:** [10.1016/j.compeleceng.2005.07.001](https://doi.org/10.1016/j.compeleceng.2005.07.001).
- **Relevance:** Hardware area/performance tradeoffs; final resource estimates require the actual target synthesis.

## DOI-bearing official technical standards

These are technical standards/guidelines, separate from the peer-reviewed papers above.

### [14] SHA-256 specification

- **Author:** National Institute of Standards and Technology.
- **Title:** Secure Hash Standard (SHS).
- **Publication / year:** FIPS 180-4, 2015.
- **DOI:** [10.6028/NIST.FIPS.180-4](https://doi.org/10.6028/NIST.FIPS.180-4).
- **Relevance:** SHA-256 algorithm/padding and known-answer verification baseline.
- **Official record:** [NIST FIPS 180-4](https://csrc.nist.gov/pubs/fips/180-4/upd1/final).

### [15] HMAC specification

- **Author:** National Institute of Standards and Technology.
- **Title:** The Keyed-Hash Message Authentication Code (HMAC).
- **Publication / year:** FIPS 198-1, 2008.
- **DOI:** [10.6028/NIST.FIPS.198-1](https://doi.org/10.6028/NIST.FIPS.198-1).
- **Relevance:** HMAC construction for shared-core controller/reference-model comparison.
- **Official record:** [NIST FIPS 198-1](https://csrc.nist.gov/pubs/fips/198-1/final). The official page carries a June 2025 planning note about proposed withdrawal/content migration; this bibliography retains the proposal's cited edition and does not assert certification or a current compliance status.

### [16] Firmware resiliency

- **Author:** Andrew Regenscheid.
- **Title:** Platform Firmware Resiliency Guidelines.
- **Publication / year:** NIST SP 800-193, 2018.
- **DOI:** [10.6028/NIST.SP.800-193](https://doi.org/10.6028/NIST.SP.800-193).
- **Relevance:** Firmware protection/detection/recovery and anti-rollback motivation. Digest/version comparison alone is not full platform resiliency.
- **Official record:** [NIST SP 800-193](https://csrc.nist.gov/pubs/sp/800/193/final).

## Metadata corrections and requirements documents

Publisher-deposited metadata identifies [1]'s author as **Omer Rana**, adds **Rene Cumplido** omitted in the proposal's [12], and identifies [13]'s second author as **A. Shoba Das** rather than the abbreviated "A. S. Das". These are bibliographic clarifications, not architectural changes. Names are transliterated to ASCII where appropriate.

The PERURI competition guidebook/template and DE10-Nano board documentation are **requirements/device specifications**, not DOI scientific evidence. They were not separately supplied here. Board/resource statements in this repository are attributed to the proposal and must be checked against the exact Quartus device report/board manual during implementation. No extra non-DOI scientific references have been added.
