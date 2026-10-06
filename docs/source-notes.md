# Ketertelusuran Proposal dan Keputusan Desain

Acuan konsep adalah *SafeTrace_Lite_PERURI_Proposal_DOI_Revisi (1).pdf*, 11 halaman, yang diberikan pemilik proyek. PDF tidak dimasukkan ke repositori karena lampiran asli serta isian identitas/kontak tim tidak diperlukan untuk dokumentasi ini. Verifikasi metadata publikasi melengkapi daftar pustaka; proposal tetap menjadi acuan arsitektur.

SHA-256 PDF sumber: `a3109a4277d083e495f03d3f41c476e26162a627e7c02eaddd0fc3f1660fa12f`. Nilai ini mengidentifikasi revisi yang ditelaah tanpa memublikasikan lampiran.

## Pemetaan Sumber

| Bagian proposal | Cakupan repositori |
| --- | --- |
| Halaman 1-2, Ringkasan Ide | Gambaran/solusi README, siklus kepercayaan, dan pembagian perangkat keras |
| Halaman 2-3, Latar Belakang dan Rumusan Masalah | Masalah, motivasi penelitian, dan batas kebaruan |
| Halaman 3-4, Model Ancaman dan MVP | Batasan README dan batas keamanan arsitektur |
| Halaman 4, Gambar 1-2 | Mermaid/PNG: transport HPS, proksi sensor tepercaya, pemeriksaan FPGA, aktuasi, audit/checkpoint |
| Halaman 4-5, Prinsip Kerja dan Modul RTL | Spesifikasi modul dan alur kerja arsitektur |
| Halaman 5-6, Format Peristiwa, Persamaan, dan Memori | Kriptografi/memori dan pengemasan peristiwa model |
| Halaman 6, Antarmuka, Keamanan, dan Area | Penguncian host, default-deny, dan inti bersama |
| Halaman 7-9, Estimasi dan Bagian 3.2 | Target README, T1-T12, dan persyaratan pengukuran |
| Halaman 9-10, Referensi [1]-[16] | Daftar pustaka DOI beserta koreksi metadata |
| Halaman 10-11, Bootcamp dan Pengembangan Lanjutan | Peta jalan README dan rencana integrasi simulasi |

## Klarifikasi Konsep

Contoh field peristiwa berjumlah 128 bit. Hash sebelumnya (256) + peristiwa (128) = 384 bit pesan sebelum padding SHA. Jadi, 384 bit bukan ukuran peristiwa yang masih harus ditambah hash sebelumnya. Kesimpulan satu blok pada proposal tetap berlaku.

Peristiwa audit mencatat keputusan gerbang. Catatan itu tidak membuktikan aktuator telah menyelesaikan tindakan atau timestamp telah diautentikasi secara fisik. `timestamp_low` merupakan field masukan demo, bukan jam tepercaya. HMAC mengautentikasi perintah; status sensor diambil secara terpisah.

## Asumsi Model dan Spesifikasi yang Belum Final

| Keputusan | Asumsi perangkat lunak dan pekerjaan RTL berikutnya |
| --- | --- |
| Pengodean perintah | Big-endian `command_id:u8`, `value:u16`, `sequence:u32`; ketujuh byte masuk ke HMAC. Model hanya mendukung ID 1 untuk persentase kecepatan. Lebar dan pengodean belum ditetapkan proposal. |
| Pengodean peristiwa | Mengikuti contoh 128 bit proposal, big-endian. Byte keputusan/alasan memakai bit 7 untuk ALLOW dan 7 bit bawah untuk enumerasi alasan model. |
| Kebijakan | Kecepatan <=80% dan suhu <=70 pada data uji. Batas kecepatan 80 berasal dari proposal; suhu 70 merupakan contoh pengujian, bukan ambang fisik wajib. |
| Pembaruan nomor urut | Perintah autentik dengan nomor baru memakai nomor itu sebelum evaluasi kebijakan, termasuk jika kebijakan menolak. HMAC tidak valid tidak memperbarui nomor. Lebar dan aturan pembaruan harus ditetapkan dalam desain RTL. |
| Genesis | Model menghitung hash label domain, ID perangkat, digest image terukur, versi masukan, dan hasil boot. Hasil boot terikat secara deterministik untuk uji perangkat lunak; format genesis/sesi perangkat keras belum final. |
| Siklus boot | Satu verifikasi boot per periode reset model. Perintah sebelum boot selesai ditolak; demo memulai operasi setelah verifikasi tersebut. |
| Reset | Kepercayaan, nomor urut, penghitung, dan log runtime dibersihkan; keluaran tidak aktif. Konfigurasi demo yang tetap dipertahankan. Identitas sesi terpisah dan anti-replay/anti-rollback persisten belum ditetapkan. Boot identik menghasilkan genesis model yang identik. |
| Checkpoint | Snapshot tetap di memori, disimpan secara independen dalam variabel pengujian. Verifikasi menerima kelanjutan log yang sah, tetapi menolak bagian terjangkar yang hilang atau tidak sesuai. Jaringan/backend belum diimplementasikan. |
| Buffer dan transaksi | Model menyimpan list Python tanpa batas kapasitas dan mengevaluasi perintah secara atomik. Kedalaman BRAM, buffer penuh, siklus penjadwal, reset di tengah transaksi, timing GPIO/PWM, dan penguncian register host tidak dimodelkan. |

## Keputusan Sebelum Integrasi RTL

1. Ikat metadata versi keamanan dengan manifest/digest image tepercaya. Versi yang diberikan HPS saja tidak membuktikan versi asli image.
2. Tetapkan persistensi nomor urut/penghitung/sesi saat reset dan rekonfigurasi, penanganan batas penghitung, serta pemilihan periode oleh backend. Prototipe hanya menetapkan kenaikan monoton dalam sesi.
3. Tetapkan penyediaan kunci/digest/kebijakan, perilaku penguncian/reset, dan perlindungan dari pembacaan atau penulisan host.
4. Tetapkan keadilan penjadwal, kepemilikan state SHA, penangkapan transaksi/backpressure, buffer peristiwa penuh, serta apakah kegagalan log harus menghambat aktuasi. Kehilangan bukti tanpa pemberitahuan tidak boleh dianggap pencatatan lengkap.
5. Tetapkan byte genesis, autentisitas/retensi checkpoint, dan pembacaan penghitung/hash yang konsisten. Transport yang dikuasai penyerang tidak boleh membentuk anchor yang dianggap tepercaya secara keliru.
6. Tetapkan prioritas reset, penyelesaian operasi autentikasi/keluaran/log yang tertunda, durasi sinyal aktuator, waktu pengambilan sensor, dan penanganan perintah tidak sah.

Daftar ini mencatat celah spesifikasi serta usulan keputusan lanjutan. Fitur keamanan produksi tambahan belum diimplementasikan.
