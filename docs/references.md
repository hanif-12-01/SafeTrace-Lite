# Referensi Ilmiah dan Standar Teknis Ber-DOI

Referensi [1]-[16] berasal dari bagian 4 proposal, halaman 9-10. Penomoran dipertahankan. Setiap entri memiliki DOI dan penjelasan relevansi terhadap proyek. Relevansi menjelaskan dasar perancangan; kinerja SafeTrace Lite belum diukur. Judul publikasi dan nama penerbit dipertahankan dalam bahasa aslinya agar sesuai metadata DOI.

Metadata bibliografi diperiksa terhadap [catatan Crossref dari penerbit](https://api.crossref.org/) untuk [1]-[13] dan halaman resmi NIST untuk [14]-[16] pada **6 Oktober 2026**. Koreksi nama penulis dijelaskan di bawah. Proposal tetap menjadi acuan utama arsitektur.

## Publikasi Ilmiah yang Ditelaah Sejawat

### [1] Keamanan Sistem Siber-Fisik Industri

- **Penulis:** Hakan Kayan, Matthew Nunes, Omer Rana, Pete Burnap, Charith Perera.
- **Judul:** Cybersecurity of Industrial Cyber-Physical Systems: A Review.
- **Publikasi / tahun:** *ACM Computing Surveys*, 54(11s), Article 229, 2022.
- **DOI:** [10.1145/3510410](https://doi.org/10.1145/3510410).
- **Relevansi:** Permukaan serangan ICPS dan dasar pemeriksaan keamanan yang terkoordinasi sepanjang siklus hidup.

### [2] Survei Keamanan Sistem Siber-Fisik

- **Penulis:** Abdulmalik Humayed, Jingqiang Lin, Fengjun Li, Bo Luo.
- **Judul:** Cyber-Physical Systems Security-A Survey.
- **Publikasi / tahun:** *IEEE Internet of Things Journal*, 4(6), 1802-1831, 2017.
- **DOI:** [10.1109/JIOT.2017.2703172](https://doi.org/10.1109/JIOT.2017.2703172).
- **Relevansi:** Hubungan kompromi siber dengan pengindraan, kendali, dan konsekuensi fisik.

### [3] Jaringan Industri

- **Penulis:** Manuel Cheminod, Luca Durante, Adriano Valenzano.
- **Judul:** Review of Security Issues in Industrial Networks.
- **Publikasi / tahun:** *IEEE Transactions on Industrial Informatics*, 9(1), 277-293, 2013.
- **DOI:** [10.1109/TII.2012.2198666](https://doi.org/10.1109/TII.2012.2198666).
- **Relevansi:** Karakteristik industri menjadi dasar pengaman ringkas untuk perintah fisik kritis.

### [4] Serangan pada Kendali Proses

- **Penulis:** Alvaro A. Cardenas, Saurabh Amin, Zong-Syun Lin, Yu-Lun Huang, Chi-Yen Huang, Shankar Sastry.
- **Judul:** Attacks against process control systems: risk assessment, detection, and response.
- **Publikasi / tahun:** *Proceedings of the 6th ACM Symposium on Information, Computer and Communications Security (ASIACCS)*, 355-366, 2011.
- **DOI:** [10.1145/1966913.1966959](https://doi.org/10.1145/1966913.1966959).
- **Relevansi:** Dasar evaluasi kondisi fisik sebagai pelengkap autentikasi pesan jaringan.

### [5] Bootstrap Aman

- **Penulis:** W. A. Arbaugh, D. J. Farber, J. M. Smith.
- **Judul:** A Secure and Reliable Bootstrap Architecture.
- **Publikasi / tahun:** *IEEE Symposium on Security and Privacy*, 65-71, 1997.
- **DOI:** [10.1109/SECPRI.1997.601317](https://doi.org/10.1109/SECPRI.1997.601317).
- **Relevansi:** Dasar rantai kepercayaan untuk memverifikasi image sebelum tahap operasi berikutnya.

### [6] Boot dan Atestasi IoT

- **Penulis:** Zhen Ling, Huaiyu Yan, Xinhui Shao, Junzhou Luo, Yiling Xu, Bryan Pearson, Xinwen Fu.
- **Judul:** Secure boot, trusted boot and remote attestation for ARM TrustZone-based IoT Nodes.
- **Publikasi / tahun:** *Journal of Systems Architecture*, 119, 102240, 2021.
- **DOI:** [10.1016/j.sysarc.2021.102240](https://doi.org/10.1016/j.sysarc.2021.102240).
- **Relevansi:** Dasar pengukuran boot dan integritas; gerbang digest SafeTrace Lite memiliki cakupan prototipe yang lebih terbatas.

### [7] Keselamatan Saat Operasi

- **Penulis:** Stanley Bak, Deepti K. Chivukula, Olugbemiga Adekunle, Mu Sun, Marco Caccamo, Lui Sha.
- **Judul:** The System-Level Simplex Architecture for Improved Real-Time Embedded System Safety.
- **Publikasi / tahun:** *15th IEEE Real-Time and Embedded Technology and Applications Symposium (RTAS)*, 99-107, 2009.
- **DOI:** [10.1109/RTAS.2009.20](https://doi.org/10.1109/RTAS.2009.20).
- **Relevansi:** Dasar pemisahan logika keselamatan kecil dari pengendali perangkat lunak kompleks. Pengendali Simplex lengkap tidak diimplementasikan di sini.

### [8] Perangkat Keras Tepercaya yang Ringan

- **Penulis:** Patrick Koeberl, Steffen Schulz, Ahmad-Reza Sadeghi, Vijay Varadharajan.
- **Judul:** TrustLite: A Security Architecture for Tiny Embedded Devices.
- **Publikasi / tahun:** *Proceedings of the Ninth European Conference on Computer Systems (EuroSys)*, 2014.
- **DOI:** [10.1145/2592798.2592824](https://doi.org/10.1145/2592798.2592824).
- **Relevansi:** Dasar batas kepercayaan perangkat keras yang ringan. SafeTrace Lite tidak mengimplementasikan arsitektur isolasi TrustLite.

### [9] Pencatatan Audit Aman

- **Penulis:** Bruce Schneier, John Kelsey.
- **Judul:** Secure Audit Logs to Support Computer Forensics.
- **Publikasi / tahun:** *ACM Transactions on Information and System Security*, 2(2), 159-176, 1999.
- **DOI:** [10.1145/317087.317089](https://doi.org/10.1145/317087.317089).
- **Relevansi:** Dasar bukti integritas untuk riwayat forensik. MVP memakai rantai hash lebih sederhana dan tidak mengklaim sifat forward-security yang setara.

### [10] Keamanan Log dan Pemotongan Riwayat

- **Penulis:** Di Ma, Gene Tsudik.
- **Judul:** A New Approach to Secure Logging.
- **Publikasi / tahun:** *ACM Transactions on Storage*, 5(1), Article 2, 2009.
- **DOI:** [10.1145/1502777.1502779](https://doi.org/10.1145/1502777.1502779).
- **Relevansi:** Dasar keamanan riwayat dan masalah pemotongan bagian akhir yang memotivasi checkpoint independen.

### [11] Konstruksi HMAC

- **Penulis:** Mihir Bellare, Ran Canetti, Hugo Krawczyk.
- **Judul:** Keying Hash Functions for Message Authentication.
- **Publikasi / tahun:** *Advances in Cryptology-CRYPTO '96*, Lecture Notes in Computer Science, 1-15, 1996.
- **DOI:** [10.1007/3-540-68697-5_1](https://doi.org/10.1007/3-540-68697-5_1).
- **Relevansi:** Dasar autentikasi pesan berkunci untuk verifikasi perintah HMAC-SHA256.

### [12] SHA-256 FPGA yang Ringkas

- **Penulis:** Rommel Garcia, Ignacio Algredo-Badillo, Miguel Morales-Sandoval, Claudia Feregrino-Uribe, Rene Cumplido.
- **Judul:** A compact FPGA-based processor for the Secure Hash Algorithm SHA-256.
- **Publikasi / tahun:** *Computers & Electrical Engineering*, 40(1), 194-202, 2014.
- **DOI:** [10.1016/j.compeleceng.2013.11.014](https://doi.org/10.1016/j.compeleceng.2013.11.014).
- **Relevansi:** Pertimbangan area/throughput serta penggunaan ulang mendasari inti bersama. Metrik publikasi bukan hasil penggunaan sumber daya SafeTrace Lite.

### [13] Pertimbangan Implementasi SHA

- **Penulis:** Imtiaz Ahmad, A. Shoba Das.
- **Judul:** Hardware implementation analysis of SHA-256 and SHA-512 algorithms on FPGAs.
- **Publikasi / tahun:** *Computers & Electrical Engineering*, 31(6), 345-360, 2005.
- **DOI:** [10.1016/j.compeleceng.2005.07.001](https://doi.org/10.1016/j.compeleceng.2005.07.001).
- **Relevansi:** Pertimbangan area/kinerja perangkat keras. Angka sumber daya akhir harus berasal dari sintesis pada target aktual.

## Standar Teknis Resmi Ber-DOI

Bagian ini berisi standar/panduan teknis resmi, dipisahkan dari publikasi ilmiah yang ditelaah sejawat di atas.

### [14] Spesifikasi SHA-256

- **Penulis:** National Institute of Standards and Technology.
- **Judul:** Secure Hash Standard (SHS).
- **Publikasi / tahun:** FIPS 180-4, 2015.
- **DOI:** [10.6028/NIST.FIPS.180-4](https://doi.org/10.6028/NIST.FIPS.180-4).
- **Relevansi:** Dasar algoritma/padding SHA-256 dan verifikasi dengan hasil acuan yang diketahui.
- **Sumber resmi:** [NIST FIPS 180-4](https://csrc.nist.gov/pubs/fips/180-4/upd1/final).

### [15] Spesifikasi HMAC

- **Penulis:** National Institute of Standards and Technology.
- **Judul:** The Keyed-Hash Message Authentication Code (HMAC).
- **Publikasi / tahun:** FIPS 198-1, 2008.
- **DOI:** [10.6028/NIST.FIPS.198-1](https://doi.org/10.6028/NIST.FIPS.198-1).
- **Relevansi:** Dasar konstruksi HMAC untuk membandingkan pengendali inti bersama dengan model referensi.
- **Sumber resmi:** [NIST FIPS 198-1](https://csrc.nist.gov/pubs/fips/198-1/final). Halaman resmi memuat catatan rencana Juni 2025 mengenai usulan pencabutan/pemindahan isi. Daftar pustaka mempertahankan edisi yang dikutip proposal dan tidak menyatakan sertifikasi atau status kepatuhan terkini.

### [16] Ketahanan Firmware

- **Penulis:** Andrew Regenscheid.
- **Judul:** Platform Firmware Resiliency Guidelines.
- **Publikasi / tahun:** NIST SP 800-193, 2018.
- **DOI:** [10.6028/NIST.SP.800-193](https://doi.org/10.6028/NIST.SP.800-193).
- **Relevansi:** Dasar perlindungan, deteksi, pemulihan firmware, dan anti-rollback. Perbandingan digest/versi saja belum memenuhi ketahanan platform secara penuh.
- **Sumber resmi:** [NIST SP 800-193](https://csrc.nist.gov/pubs/sp/800/193/final).

## Koreksi Metadata dan Dokumen Persyaratan

Metadata penerbit mengidentifikasi penulis [1] sebagai **Omer Rana**, menambahkan **Rene Cumplido** yang terlewat pada [12] proposal, dan mengidentifikasi penulis kedua [13] sebagai **A. Shoba Das**, bukan singkatan "A. S. Das". Koreksi ini bersifat bibliografis dan tidak mengubah arsitektur. Nama ditransliterasikan ke ASCII sesuai kebutuhan.

Panduan/template kompetisi PERURI dan dokumentasi board DE10-Nano merupakan **persyaratan atau spesifikasi perangkat**, dipisahkan dari bukti ilmiah ber-DOI. Dokumen tersebut tidak diberikan secara terpisah. Pernyataan board/sumber daya di repositori mengacu pada proposal dan harus dicocokkan dengan laporan device Quartus serta manual board saat implementasi. Referensi ilmiah tambahan tanpa DOI tidak ditambahkan.
