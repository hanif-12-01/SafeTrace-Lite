# Rencana Verifikasi

Status: **verifikasi perangkat keras masih direncanakan**. Sumber utama: bagian **3.2 Rencana Pengujian**, halaman 7-9 proposal. Referensi Python memeriksa harapan fungsional; RTL, timing, bus, dan keluaran fisik belum diimplementasikan. Nama sinyal berikut merupakan rencana observasi, bukan sinyal pada bitstream yang sudah tersedia.

## Skenario Penerimaan T1-T12

Kecuali dinyatakan lain, konfigurasikan digest image tepercaya, kunci prototipe, versi minimum, batas kecepatan 80%, dan ambang sensor aman sebelum lock. Uji runtime dimulai setelah boot valid. Data uji model memakai ambang suhu 70 sebagai contoh perangkat lunak. Periksa keputusan, perubahan state, dan peristiwa bersama-sama.

### T1 — Image Awal Valid

| Aspek | Rencana |
| --- | --- |
| Tujuan | Menetapkan kepercayaan operasi hanya untuk image/versi yang diterima. |
| Prasyarat | Reset menghasilkan BLOCK; acuan digest dan versi minimum telah dikonfigurasi/dikunci. |
| Stimulus masukan | Image lengkap dengan digest sesuai dan versi >=minimum. |
| Perilaku yang diharapkan | Digest/versi lolos; gerbang dapat memasuki runtime, tetapi boot saja belum mengotorisasi perintah. |
| Sinyal keluaran yang diharapkan | `SYSTEM_TRUSTED=1`, boot selesai; `ACTUATOR_ENABLE=0` hingga keputusan runtime valid. |
| Kriteria lulus/gagal | Kepercayaan aktif hanya setelah verifikasi lengkap berhasil; aktuator tidak aktif selama hashing. |
| Metode verifikasi yang direncanakan | Pemeriksaan digest/versi Python; streaming lengkap cocotb terhadap acuan; waveform untuk waktu enable. |

### T2 — Image Firmware Dimodifikasi

| Aspek | Rencana |
| --- | --- |
| Tujuan | Menolak perubahan byte image. |
| Prasyarat | Digest berasal dari image asli; keluaran awal BLOCK. |
| Stimulus masukan | Ubah satu bit image; versi tetap memenuhi minimum. |
| Perilaku yang diharapkan | Digest tidak sesuai; trust tidak aktif dan percobaan perintah tetap BLOCK. |
| Sinyal keluaran yang diharapkan | `SYSTEM_TRUSTED=0`, status digest mismatch, `ACTUATOR_ENABLE=0`, BLOCK. |
| Kriteria lulus/gagal | Image lengkap dengan digest berbeda tetap tidak tepercaya; boot gagal tidak memakai state valid sebelumnya. |
| Metode verifikasi yang direncanakan | Uji perubahan bit Python; streaming RTL dengan digest independen dan assertion keluaran; demo LED/status board. |

### T3 — Rollback Firmware

| Aspek | Rencana |
| --- | --- |
| Tujuan | Menegakkan versi minimum yang dikonfigurasi. |
| Prasyarat | Digest image sesuai; versi minimum terlindungi. |
| Stimulus masukan | Digest valid, tetapi versi masukan <minimum. |
| Perilaku yang diharapkan | Gerbang versi menolak meskipun digest lolos. |
| Sinyal keluaran yang diharapkan | `ROLLBACK=1`, `SYSTEM_TRUSTED=0`, BLOCK, `ACTUATOR_ENABLE=0`. |
| Kriteria lulus/gagal | Versi lebih rendah selalu ditolak; nilai sama diterima dalam variasi T1. Pengujian ini memeriksa perbandingan, bukan autentikasi metadata versi. |
| Metode verifikasi yang direncanakan | Kasus versi Python; batas komparator RTL dan register terkunci; pengikatan manifest bertanda tangan diuji pada pengembangan lanjutan. |

### T4 — Perintah Autentik Valid

| Aspek | Rencana |
| --- | --- |
| Tujuan | Mengizinkan tindakan autentik, baru, dan aman serta mencatat buktinya. |
| Prasyarat | Boot tepercaya, nomor terakhir lebih rendah, suhu aman. |
| Stimulus masukan | HMAC valid atas seluruh payload, nomor baru, kecepatan=60 dengan maksimum=80. |
| Perilaku yang diharapkan | HMAC, kebaruan nomor, dan kebijakan lolos; nomor diperbarui; peristiwa ALLOW tercatat. |
| Sinyal keluaran yang diharapkan | `HMAC_VALID=1`, `FRESH_SEQUENCE=1`, `POLICY_VALID=1`, ALLOW, `ACTUATOR_ENABLE=1`; event-valid, penghitung meningkat, dan hash baru setelah log selesai. |
| Kriteria lulus/gagal | Nilai perintah benar diteruskan, tepat satu peristiwa dicatat, hash cocok dengan perhitungan independen. |
| Metode verifikasi yang direncanakan | Pemeriksaan keputusan/rantai Python; transaksi menyeluruh cocotb; SignalTap dan observasi LED/PWM/driver tegangan rendah. |

### T5 — Perintah Palsu

| Aspek | Rencana |
| --- | --- |
| Tujuan | Menolak HMAC salah tanpa meracuni state replay. |
| Prasyarat | Boot tepercaya dan nomor terakhir diketahui. |
| Stimulus masukan | Tag salah atau ID/nilai/nomor urut diubah setelah penandatanganan HMAC. |
| Perilaku yang diharapkan | BLOCK dengan AUTH_FAIL; peristiwa dicatat; nomor terakhir tidak berubah. |
| Sinyal keluaran yang diharapkan | `HMAC_VALID=0`, BLOCK, `reason_code=AUTH_FAIL`, `ACTUATOR_ENABLE=0`; pembaruan peristiwa/penghitung/hash. |
| Kriteria lulus/gagal | Tidak ada aktuasi atau pembaruan nomor tanpa autentikasi; perubahan payload/tag terdeteksi. |
| Metode verifikasi yang direncanakan | Uji tag salah/semua field Python; vektor HMAC independen dan panjang tidak sah pada cocotb; skenario serangan board. |

### T6 — Serangan Replay

| Aspek | Rencana |
| --- | --- |
| Tujuan | Menolak nomor autentik yang sama atau lebih lama. |
| Prasyarat | Perintah autentik baru telah menetapkan `last_sequence`. |
| Stimulus masukan | HMAC valid dengan nomor ==terakhir atau <terakhir. |
| Perilaku yang diharapkan | BLOCK dengan REPLAY; nomor tidak mundur; penolakan dicatat. |
| Sinyal keluaran yang diharapkan | `HMAC_VALID=1`, `FRESH_SEQUENCE=0`, BLOCK, `reason_code=REPLAY`, `ACTUATOR_ENABLE=0`. |
| Kriteria lulus/gagal | Nomor sama/lama ditolak; nomor baru diterima jika aman; nomor tinggi tanpa autentikasi tidak meracuni state. |
| Metode verifikasi yang direncanakan | Uji nomor sama/lama Python; timing pembaruan, batas maksimum/tanpa wrap, dan pembacaan state RTL. Kebaruan lintas reset memerlukan desain sesi/persistensi terpisah. |

### T7 — Tepat pada Batas Aman

| Aspek | Rencana |
| --- | --- |
| Tujuan | Memastikan batas keselamatan bersifat inklusif. |
| Prasyarat | Boot tepercaya, HMAC valid/nomor baru, sensor aman, batas kecepatan=80. |
| Stimulus masukan | Kecepatan=80; variasi suhu tepat sama dengan ambang. |
| Perilaku yang diharapkan | Nilai sama dengan batas lolos; peristiwa ALLOW dicatat. |
| Sinyal keluaran yang diharapkan | `POLICY_VALID=1`, ALLOW, `ACTUATOR_ENABLE=1`. |
| Kriteria lulus/gagal | Nilai tepat batas diizinkan dan keluaran tetap sesuai nilai perintah yang diautentikasi. |
| Metode verifikasi yang direncanakan | Uji kesamaan batas Python; komparator/nilai keluaran cocotb; observasi hasil kebijakan SignalTap. |

### T8 — Melebihi Batas Aman

| Aspek | Rencana |
| --- | --- |
| Tujuan | Menolak nilai tepat di atas batas walaupun autentik. |
| Prasyarat | Boot tepercaya, HMAC valid/nomor baru, sensor aman, batas=80. |
| Stimulus masukan | Kecepatan=81; demo board dapat memakai 100. |
| Perilaku yang diharapkan | BLOCK dengan POLICY; dicatat. Pembaruan nomor mengikuti aturan final; model memakai nomor autentik baru meskipun kebijakan menolak. |
| Sinyal keluaran yang diharapkan | `HMAC_VALID=1`, `FRESH_SEQUENCE=1`, `POLICY_VALID=0`, BLOCK, `reason_code=POLICY`, `ACTUATOR_ENABLE=0`. |
| Kriteria lulus/gagal | Tidak ada aktuasi untuk nilai 81 atau lebih; alasan penolakan dan catatan audit benar. |
| Metode verifikasi yang direncanakan | Uji satu satuan di atas batas Python; komparator, peristiwa, dan assertion keluaran RTL; demo perintah tidak aman. |

### T9 — Kondisi Sensor Tidak Aman

| Aspek | Rencana |
| --- | --- |
| Tujuan | Menolak perintah autentik yang nilainya aman saat kondisi fisik tidak aman. |
| Prasyarat | Boot tepercaya, tag valid/nomor baru, nilai dalam batas. |
| Stimulus masukan | Suhu proksi tepercaya >ambang yang dikonfigurasi. |
| Perilaku yang diharapkan | BLOCK dengan POLICY berdasarkan snapshot sensor; snapshot tersebut dicatat. |
| Sinyal keluaran yang diharapkan | `POLICY_VALID=0`, BLOCK, `reason_code=POLICY`, `ACTUATOR_ENABLE=0`. |
| Kriteria lulus/gagal | Konteks tidak aman menolak perintah; field sensor peristiwa sesuai sampel yang dipakai untuk keputusan. |
| Metode verifikasi yang direncanakan | Ambang Python; kesamaan/melebihi batas dan konsistensi snapshot cocotb; proksi sakelar/ADC/GPIO board. Pemalsuan sebelum antarmuka tetap di luar cakupan. |

### T10 — Perubahan Log

| Aspek | Rencana |
| --- | --- |
| Tujuan | Mendeteksi bukti tersimpan yang berubah saat diverifikasi. |
| Prasyarat | Peristiwa/hash tersedia; genesis/checkpoint disimpan secara independen. |
| Stimulus masukan | Ubah satu bit peristiwa, termasuk keputusan; coba hitung ulang hash tersimpan dengan checkpoint tepercaya tetap. |
| Perilaku yang diharapkan | Digest atau hash terjangkar tidak cocok; riwayat ditolak. |
| Sinyal keluaran yang diharapkan | Verifikasi gagal / `tamper_flag=1`; verifikasi audit tidak berarti aktuasi. |
| Kriteria lulus/gagal | Catatan berubah ditolak terhadap acuan tepercaya; rantai bersih diterima. Perilaku/reset tamper flag harus sesuai spesifikasi pengendali final. |
| Metode verifikasi yang direncanakan | Perubahan salinan log dan rantai yang dihitung ulang di Python; mode verify RTL; demo salinan log board. |

### T11 — Pemotongan Bagian Akhir Log

| Aspek | Rencana |
| --- | --- |
| Tujuan | Mendeteksi riwayat yang lebih lama daripada checkpoint independen. |
| Prasyarat | Backend/data uji mempertahankan `{device_id, counter=105, chain_head_at_105}`. |
| Stimulus masukan | Log berakhir pada 104, dengan hash bagian awal tetap konsisten. |
| Perilaku yang diharapkan | Penghitung checkpoint melebihi riwayat tersedia; pemotongan/ketidaksesuaian dilaporkan. |
| Sinyal keluaran yang diharapkan | Ketidaksesuaian verifikasi/checkpoint atau peringatan pemotongan backend. `tamper_flag` FPGA memerlukan jalur pelaporan backend-ke-FPGA yang eksplisit dan tidak diasumsikan tersedia. |
| Kriteria lulus/gagal | Pemotongan terjangkar ditolak; 105 catatan utuh dan kelanjutannya yang sah diterima. Tidak mengklaim deteksi semua penghapusan bagian akhir tanpa anchor. |
| Metode verifikasi yang direncanakan | Contoh 105→104, hash palsu/ID salah/kelanjutan Python; integrasi HPS/backend dan uji snapshot checkpoint konsisten. |

### T12 — Perilaku Reset

| Aspek | Rencana |
| --- | --- |
| Tujuan | Mengembalikan kondisi aman dan mencegah ALLOW lama setelah reset. |
| Prasyarat | Uji idle, runtime tepercaya, SHA/HMAC aktif, keluaran tertunda, dan log yang belum selesai. |
| Stimulus masukan | Reset pada setiap tahap transaksi RTL, termasuk tepat sebelum decision-valid. |
| Perilaku yang diharapkan | Keluaran BLOCK; trust/validitas dan kepemilikan SHA dibersihkan; operasi tidak lengkap tidak menghidupkan keputusan lama. Persistensi/lock/sesi reset harus ditetapkan terpisah. |
| Sinyal keluaran yang diharapkan | `ACTUATOR_ENABLE=0`, `SYSTEM_TRUSTED=0`, tidak ada ALLOW/digest/event-valid lama, status reset aman. |
| Kriteria lulus/gagal | Keluaran tidak aktif selama/setelah reset sampai boot dan perintah autentik aman baru; pembaruan peristiwa parsial memiliki perilaku yang ditetapkan. |
| Metode verifikasi yang direncanakan | Python hanya memeriksa reset di antara pemanggilan atomik. Reset tengah transaksi, timing asinkron, serta efek bus/domain clock memerlukan cocotb/RTL dan SignalTap; belum diuji. |

## Perangkat dan Tahap Verifikasi

| Tahap dan perangkat | Bukti yang diperlukan sebelum dinyatakan selesai |
| --- | --- |
| Referensi pustaka standar Python | Keluaran unittest nyata untuk keputusan, serialisasi, dan verifikasi anchor; tanpa inferensi timing/sumber daya. |
| Verilator / ModelSim | Kompilasi RTL nyata, simulasi unit/integrasi, serta waveform/assertion yang bermakna. |
| cocotb + Python | Mengendalikan port nyata, membandingkan digest/tag/keputusan/byte peristiwa dengan acuan independen, handshake dan tahap reset. |
| Intel Quartus Prime + Platform Designer | Build 5CSEBA6U23I7, laporan sintesis/fitter, peta register, batas timing, laporan 50 MHz, dan Power Analyzer jika daya dilaporkan. |
| SignalTap Logic Analyzer | FSM, permintaan/validitas/pemilik SHA, nomor urut, kebijakan, gerbang keluaran, penghitung, hash/tamper pada board. |
| Demonstrasi fisik | Startup valid/modifikasi/rollback; perintah aman/tidak aman/replay; log berubah/pemotongan terjangkar; LED/PWM atau motor tegangan rendah melalui driver. |

Sebelum integrasi RTL, jalankan vektor SHA/HMAC dengan hasil acuan yang diketahui secara independen. Uji padding pesan 55/56/63/64 byte dan image multiblok. Periksa kepemilikan layanan SHA saat persaingan, perlindungan lock/pembacaan konfigurasi, masukan tidak sah, backpressure BRAM, dan batas penghitung. Identitas transaksi harus dijaga agar validitas dari perintah berbeda tidak digabung menjadi ALLOW.

## Target Rekayasa dan Pelaporan

Seluruh angka merupakan **target rekayasa — bukan hasil pengukuran**: 50 MHz; <=4.000 ALM; <=5.000 FF; <=128 Kbit BRAM; 0 DSP; satu blok SHA <5 mikrodetik; HMAC pendek <25 mikrodetik; kebijakan <=5 siklus setelah autentikasi/nomor urut; log satu blok ditambah kendali. Waktu tunggu penjadwal dan transfer host harus diperhitungkan terpisah pada latensi menyeluruh.

Target keberhasilan: seluruh vektor SHA/HMAC yang ditetapkan lulus; T2/T3/T5/T6/T8/T9 menghasilkan BLOCK; T10/T11 menghasilkan peringatan audit yang benar; reset/tidak tepercaya/error menjaga keluaran tidak aktif; penghitung/hash konsisten. Demo menyeluruh direncanakan 3-5 menit. Target FPGA tersebut belum diukur dalam repositori ini.

Laporan berikutnya harus menyebut commit, versi perangkat, device/batas clock, kumpulan vektor, skenario lulus/gagal, siklus teramati, penggunaan sumber daya, dan batasan. Waveform, foto board, benchmark, dan laporan sintesis harus berasal dari pelaksanaan nyata. [Cakupan perangkat lunak](../tests/README.md) menjelaskan bagian yang dapat diperiksa saat ini.
