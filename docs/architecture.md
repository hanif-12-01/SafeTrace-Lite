# Usulan Arsitektur SafeTrace Lite

Status: **Usulan Arsitektur / Praimplementasi**. Sumber utama: bagian 3.1 proposal, halaman 4-7, dengan batasan dari halaman 3-4. Port berikut merupakan antarmuka logis yang direncanakan, bukan deklarasi RTL yang sudah diimplementasikan. Lebar yang dinyatakan dalam proposal menjadi ketentuan; detail lain masih perlu ditetapkan. [Catatan sumber](source-notes.md) memuat keputusan terbuka dan asumsi model perangkat lunak.

## A. Gambaran Sistem

Siklus kepercayaan adalah **Image Firmware → Boot Integrity Gate → Runtime Action Guard → Aktuator → TrustLog → Penyimpanan Audit → Verifikasi Backend**. Urutan ini menunjukkan ketergantungan kepercayaan. TrustLog menerima keputusan FPGA, bukan laporan umpan balik fisik aktuator. Catatan ALLOW membuktikan keputusan gerbang; catatan tersebut tidak membuktikan motor telah menyelesaikan gerakan.

1. HPS mengirim image aplikasi uji dan versi ke FPGA. Keluaran tetap BLOCK.
2. Boot Integrity Gate memakai inti SHA-256 bersama untuk membandingkan digest image dengan konfigurasi tepercaya dan memeriksa `version >= min_version`.
3. Keberhasilan menetapkan `SYSTEM_TRUSTED`; kegagalan mempertahankan nilai rendah. Hasil boot menjadi dasar genesis rantai audit; pengodean persisnya belum ditetapkan.
4. HPS membawa frame perintah dari pengirim tepercaya: `command_id`, `value`, `sequence`, dan tag HMAC. FPGA mengautentikasi payload, memeriksa kebaruan nomor urut, lalu mengevaluasi keselamatan dengan snapshot sensor.
5. Output Gate hanya mengizinkan perintah jika seluruh kondisi terpenuhi. Perintah yang ditolak tidak mengaktifkan keluaran.
6. Event Formatter membentuk catatan keputusan/alasan dengan lebar tetap. TrustLog menaikkan penghitung dan memperpanjang rantai hash untuk ALLOW maupun BLOCK.
7. Catatan terbaru disimpan pada BRAM FPGA dan disinkronkan ke HPS/penyimpanan eksternal. Secara berkala HPS mengirim `{device_id, event_counter, chain_head}` ke backend.
8. Verifikasi menghitung ulang rantai dan membandingkan penghitung/hash pada checkpoint tepercaya. Riwayat yang berakhir sebelum checkpoint tersimpan menunjukkan pemotongan atau rollback.

![Usulan arsitektur SafeTrace Lite](block-diagram.png)

## B. Arsitektur Perangkat Keras

| Komponen | Peran dan batas yang direncanakan |
| --- | --- |
| HPS ARM DE10-Nano | Antarmuka pengguna, streaming image, transport perintah, sinkronisasi log, dan penerusan checkpoint. Keputusan akhir autentikasi/keselamatan tetap pada FPGA. |
| Fabric FPGA | Boot, HMAC, replay, kebijakan, gerbang keluaran, format peristiwa, TrustLog, konfigurasi tepercaya, dan state runtime. |
| Bridge HPS-to-FPGA | Lightweight HPS-to-FPGA bridge membawa transaksi Avalon-MM; Platform Designer mengintegrasikan register dan streaming host. Peta register/protokol transfer belum final. |
| Inti SHA-256 bersama | Satu mesin dengan blok masukan 512 bit dan digest 256 bit, digunakan bergantian untuk boot, HMAC, dan log. |
| Penjadwal SHA | Memberikan kepemilikan layanan dan meneruskan hasil. Konteks transaksi multiblok harus terjaga; arbitrasi dan batas waktu tunggu masih perlu dirancang. |
| Konfigurasi tepercaya | ROM/register FPGA berisi digest firmware 256 bit, kunci HMAC prototipe 256 bit, versi minimum, dan kebijakan. Provisioning dilakukan sebelum lock; perubahan host ditolak setelah lock. Kunci tidak boleh dibaca host. |
| Antarmuka perintah | Pengirim tepercaya membentuk HMAC; HPS membawa payload/tag. ID, nilai, dan nomor urut harus diautentikasi bersama dalam satu pengodean baku. |
| Antarmuka sensor | Proksi tepercaya berupa sakelar/ADC/GPIO untuk demo. Pemeriksaan keselamatan memakai snapshot yang konsisten; autentisitas sebelum batas ini diasumsikan. |
| Antarmuka keluaran | GPIO/PWM menuju LED atau driver motor bertegangan rendah. Pin FPGA tidak langsung menggerakkan beban daya besar. Keluaran awal tidak aktif. |
| Penyimpanan audit | 16-64 peristiwa terbaru pada M10K/BRAM; HPS/penyimpanan eksternal menyimpan peristiwa/hash jangka panjang. Penyimpanan dapat diverifikasi, tetapi tidak otomatis tepercaya. |
| Checkpoint backend | Menyimpan anchor independen berupa ID/penghitung/hash. Keamanan penuh backend dan autentikasi checkpoint produksi berada di luar MVP. |

Garis putus-putus pada diagram menunjukkan hubungan logis permintaan/hasil kriptografi. Definisi bus/register fisik serta kontrak streaming dan backpressure masih perlu dirancang.

## C. Spesifikasi Modul RTL

### `sha256_core`

| Aspek | Spesifikasi yang direncanakan |
| --- | --- |
| Tujuan | Mesin SHA-256 dasar yang digunakan bersama, tanpa mereplikasi tiga inti. |
| Masukan | `block_in[511:0]`, `init`, `next`, clock/reset, dan handshake permintaan yang akan ditetapkan. |
| Keluaran | `digest[255:0]`, `ready`, `digest_valid`. |
| Keadaan internal | Word hash kerja, jadwal pesan, penghitung putaran, state chaining, dan FSM pemrosesan. |
| Ketergantungan | Kontrak kompresi/padding SHA-256 standar; penjadwal memasok blok dengan pembingkaian yang benar. |
| Perilaku yang diharapkan | Menerima blok saat ready; menghasilkan digest terkait dengan valid aktif; mendukung blok awal/lanjutan tanpa mencampur klien. Pemilik proses padding harus ditetapkan. |
| Rencana verifikasi | Vektor dengan hasil acuan yang diketahui; pesan kosong/pendek/multiblok; batas padding 55/56/63/64 byte; init/next/reset dan waktu hasil. |

### `sha_scheduler`

| Aspek | Spesifikasi yang direncanakan |
| --- | --- |
| Tujuan | Mengatur permintaan boot, HMAC, dan TrustLog menuju satu inti SHA. |
| Masukan | `request_boot`, `request_hmac`, `request_log`, blok/kendali klien, serta ready/valid inti. |
| Keluaran | Grant klien, permintaan SHA terpilih, digest/valid yang diteruskan, serta status busy. |
| Keadaan internal | Pemilik dan FSM arbitrasi; konteks transaksi atau retensi kepemilikan. |
| Ketergantungan | `sha256_core` dan ketiga pengendali permintaan. |
| Perilaku yang diharapkan | Tepat satu pemilik; digest hanya kembali ke pemiliknya. State multiblok konsisten; reset membersihkan grant. Proposal belum menetapkan prioritas/keadilan. |
| Rencana verifikasi | Permintaan bersamaan, image panjang bersaing dengan runtime/log, backpressure, isolasi pemilik, batas penundaan, dan reset saat busy. |

### `boot_integrity_ctrl`

| Aspek | Spesifikasi yang direncanakan |
| --- | --- |
| Tujuan | Memverifikasi digest image dan versi minimum sebelum operasi diizinkan. |
| Masukan | `image_stream`, `image_last`, `version`, `trusted_digest`, `min_version`, reset, dan handshake SHA. |
| Keluaran | `system_trusted`, status digest/rollback, dan hasil boot untuk genesis. |
| Keadaan internal | FSM streaming/padding, penghitung byte, perbandingan digest, hasil versi, dan latch kepercayaan. |
| Ketergantungan | `sha_scheduler`, konfigurasi tepercaya, dan antarmuka streaming host. |
| Perilaku yang diharapkan | Mulai tidak tepercaya; trust aktif setelah image lengkap, digest, dan versi valid. Kepercayaan lama tidak boleh tersisa setelah verifikasi gagal atau reset. |
| Rencana verifikasi | T1-T3, image tidak lengkap, batas padding, backpressure, dan reset saat hashing/perbandingan. |

### `hmac_ctrl`

| Aspek | Spesifikasi yang direncanakan |
| --- | --- |
| Tujuan | Memverifikasi HMAC-SHA256 pengirim atas seluruh payload perintah. |
| Masukan | `cmd_payload`, `auth_tag`, `key_ref` terlindungi, permintaan/reset, dan hasil SHA. |
| Keluaran | `auth_valid`, status selesai, dan kegagalan autentikasi. |
| Keadaan internal | FSM hash bagian dalam/luar, persiapan ipad/opad, digest antara, dan tag yang ditangkap. |
| Ketergantungan | `sha_scheduler`, kunci terlindungi, dan serialisasi perintah baku. |
| Perilaku yang diharapkan | Mengikuti konstruksi HMAC; seluruh 256 bit tag dibandingkan sebelum valid. Validitas lama dibersihkan pada setiap transaksi. |
| Rencana verifikasi | Vektor acuan independen, perubahan payload/tag/kunci, autentikasi semua field, pesan pendek/multiblok, dan reset. |

### `replay_guard`

| Aspek | Spesifikasi yang direncanakan |
| --- | --- |
| Tujuan | Memastikan nomor urut autentik meningkat secara monoton. |
| Masukan | `seq_in`, status autentikasi selesai/valid, serta kendali transaksi/reset. |
| Keluaran | `seq_valid`, alasan/status replay, dan pembacaan nomor terakhir jika diekspos. |
| Keadaan internal | `last_seq`; lebar, nilai awal, serta siklus reset/sesi belum final. |
| Ketergantungan | `hmac_ctrl`, penangkapan perintah, serta kendali pembaruan state/keluaran/peristiwa. |
| Perilaku yang diharapkan | Terima hanya `seq_in > last_seq`. Masukan tidak autentik tidak boleh memajukan state; state tidak mundur atau menerima wrap secara diam-diam. Pemakaian nomor baru untuk perintah yang ditolak kebijakan masih perlu ditetapkan. |
| Rencana verifikasi | T6, nomor sama/lama/baru, peracunan state dengan tag palsu, batas maksimum, dan reset/sesi. |

### `policy_engine`

| Aspek | Spesifikasi yang direncanakan |
| --- | --- |
| Tujuan | Pemeriksaan keselamatan deterministik memakai komparator/FSM/register. |
| Masukan | `cmd_id`, `cmd_value`, `sensor_state` tepercaya, register ambang, dan kendali valid. |
| Keluaran | `policy_valid`, `reason_code`. |
| Keadaan internal | Snapshot perintah/sensor dan FSM evaluasi jika diperlukan. |
| Ketergantungan | Konfigurasi kebijakan terkunci, perintah autentik dengan nomor baru, dan antarmuka sensor. |
| Perilaku yang diharapkan | Memeriksa daftar perintah yang diizinkan dan batas nilai/sensor, misalnya kecepatan <=80% dan suhu <=ambang. Perintah tidak dikenal ditolak; daftar final belum ditetapkan. |
| Rencana verifikasi | T7-T9, seluruh ID yang didukung, nilai sama dengan/melebihi batas satu satuan, konsistensi snapshot, dan jalur kesalahan. |

### `output_gate`

| Aspek | Spesifikasi yang direncanakan |
| --- | --- |
| Tujuan | Menetapkan keputusan akhir ALLOW/BLOCK dan membatasi aktuasi. |
| Masukan | `system_trusted`, `auth_valid`, `seq_valid`, `policy_valid`, permintaan keluaran yang ditangkap, dan reset/error. |
| Keluaran | ALLOW/BLOCK, `ACTUATOR_ENABLE`/GPIO/PWM terkendali, dan keputusan peristiwa. |
| Keadaan internal | Validitas transaksi/latch keputusan; keluaran pulsa atau ditahan belum ditetapkan. |
| Ketergantungan | Hasil boot, HMAC, replay, dan kebijakan yang terkait transaksi yang sama. |
| Perilaku yang diharapkan | ALLOW hanya jika seluruh kondisi benar. Reset/tidak tepercaya/error menghasilkan BLOCK tanpa enable lama. |
| Rencana verifikasi | Tabel seluruh kombinasi kondisi, T4-T9, T12, pemisahan validitas antartransaksi, dan timing keluaran. |

### `event_formatter`

| Aspek | Spesifikasi yang direncanakan |
| --- | --- |
| Tujuan | Membentuk bukti keputusan ALLOW/BLOCK dengan lebar tetap. |
| Masukan | `counter`, `timestamp`, perintah, snapshot sensor, keputusan/alasan, dan versi firmware ringkas. |
| Keluaran | Catatan peristiwa <=128 bit, record-valid, dan handshake penerimaan yang direncanakan. |
| Keadaan internal | Field peristiwa yang ditangkap dan validitas buffer. |
| Ketergantungan | `output_gate`, state runtime, buffer TrustLog, dan format peristiwa baku. |
| Perilaku yang diharapkan | Mencatat snapshot yang sama dengan dasar keputusan, termasuk penolakan. Peristiwa tertunda tidak boleh tertimpa tanpa pemberitahuan. |
| Rencana verifikasi | Pengemasan bit/endianness, batas field, alasan ALLOW/BLOCK, batas penghitung, dan backpressure penerima. |

### `trustlog_ctrl`

| Aspek | Spesifikasi yang direncanakan |
| --- | --- |
| Tujuan | Memperpanjang rantai hash, mengelola peristiwa terbaru, dan menyediakan verifikasi/checkpoint. |
| Masukan | `prev_hash`, `event_record`, bahan genesis boot, hasil SHA, serta masukan catatan/hash mode verify. |
| Keluaran | `current_hash`, penghitung peristiwa, peristiwa/hash terbuffer, `tamper_flag`, dan snapshot checkpoint. |
| Keadaan internal | Hash sebelumnya/terkini 256 bit, penghitung, penunjuk ring buffer, serta FSM hashing/verifikasi. |
| Ketergantungan | `event_formatter`, `sha_scheduler`, M10K/BRAM, dan register host. |
| Perilaku yang diharapkan | Satu pembaruan peristiwa/penghitung/hash dilakukan atomik setelah hash selesai. Ketidaksesuaian hasil verifikasi menetapkan status perubahan. Host membaca pasangan penghitung/hash yang konsisten. |
| Rencana verifikasi | T10-T11, rantai deterministik, urutan berubah/catatan hilang, hash palsu, perputaran buffer, ekspor bersamaan dengan hash, dan reset di tengah pembaruan. |

### `avalon_mm_regs`

| Aspek | Spesifikasi yang direncanakan |
| --- | --- |
| Tujuan | Kendali/status HPS, konfigurasi kebijakan, dan akses audit/checkpoint. |
| Masukan | Read/write/address/data/byte-enable Avalon-MM dan status internal. |
| Keluaran | Data baca, wait/response sesuai kebutuhan, kendali streaming/konfigurasi yang diterima, serta pembacaan checkpoint. |
| Keadaan internal | Lock konfigurasi, register penampung transport, status, dan kendali snapshot. |
| Ketergantungan | Lightweight HPS bridge, semua pengendali, dan konfigurasi tepercaya. |
| Perilaku yang diharapkan | Menolak penulisan host ke digest/kunci/versi minimum/kebijakan setelah lock. Kunci tidak terbaca; proposal juga menyatakan kunci/digest dilindungi dari pembacaan setelah lock. Pisahkan status verifikasi publik dari isi terlindungi. |
| Rencana verifikasi | Penegakan lock, penolakan baca/tulis, alamat salah, byte-enable, transaksi parsial, snapshot konsisten, dan siklus lock/reset. |

## D. Alur Kriptografi

Simbol `||` berarti penggabungan byte baku; `C_0` adalah genesis yang terkait hasil boot. Untuk peristiwa keputusan `Event_i`:

$$
C_i = \operatorname{SHA256}(C_{i-1} \parallel \operatorname{Event}_i)
$$

`C_{i-1}` adalah hash terakhir sebelumnya sebesar 256 bit; `Event_i` adalah peristiwa berlebar tetap yang mencakup penghitung; `C_i` adalah hash baru 256 bit. Penghitung meningkat satu kali untuk setiap peristiwa yang selesai dicatat. Proposal belum menentukan byte genesis, pengikatan perangkat/sesi, dan persistensinya.

Untuk payload perintah `m` dan kunci `K`:

$$
\operatorname{HMAC}_{K}(m) = \operatorname{SHA256}((K' \oplus opad) \parallel \operatorname{SHA256}((K' \oplus ipad) \parallel m))
$$

`K'` adalah kunci yang ditambah byte nol hingga berukuran satu blok SHA-256, yaitu 64 byte; jika kunci melebihi satu blok, hash dihitung terlebih dahulu sesuai aturan HMAC. ipad/opad adalah mask byte standar. MVP menggunakan kunci 256 bit. Payload/tag ditangkap sekali agar autentikasi, nomor urut, dan kebijakan merujuk perintah yang sama.

$$
\mathrm{ALLOW}=\mathrm{SYSTEM\_TRUSTED}\land\mathrm{HMAC\_VALID}\land\mathrm{FRESH\_SEQUENCE}\land\mathrm{POLICY\_VALID}
$$

`SYSTEM_TRUSTED` menunjukkan pemeriksaan digest/versi boot telah berhasil; `HMAC_VALID` menunjukkan seluruh tag sesuai; `FRESH_SEQUENCE` menunjukkan nomor urut meningkat; `POLICY_VALID` menunjukkan nilai/sensor aman. HMAC gagal mencegah pembaruan nomor urut. Kebijakan dievaluasi setelah kebaruan nomor. Keputusan/alasan diteruskan ke gerbang keluaran dan TrustLog.

### Format Peristiwa dan Padding SHA

Contoh pada halaman 5 proposal berjumlah **128 bit**:

| Field | Bit |
| --- | --- |
| Penghitung peristiwa | 32 |
| Timestamp bagian rendah | 32 |
| ID perintah | 8 |
| Nilai perintah | 16 |
| Status sensor | 16 |
| Keputusan dan alasan | 8 |
| Versi firmware/keamanan ringkas | 16 |

Hash sebelumnya 256 bit + peristiwa 128 bit = **384 bit pesan**. Padding SHA menambahkan satu bit `1`, 63 bit nol, dan panjang pesan 64 bit: total satu blok 512 bit. Perhitungan ini memperjelas kalimat proposal mengenai "payload 384 bit" tanpa mengubah desain peristiwa. Peristiwa lebih panjang dapat membutuhkan blok tambahan. Pemrosesan satu blok merupakan target rekayasa, bukan jaminan latensi terukur.

## E. Arsitektur Memori

| Komponen | Lokasi dan ukuran yang direncanakan | Siklus hidup dan akses |
| --- | --- | --- |
| Digest firmware tepercaya | Register/ROM FPGA, 256 bit | Acuan yang diprovisikan dan dilindungi setelah lock; digunakan pengendali boot. |
| Kunci HMAC | Register/ROM FPGA, 256 bit pada MVP | Rahasia demo yang diprovisikan; tidak dibaca host dan tidak ditulis host setelah lock. |
| Versi keamanan minimum | Register/ROM FPGA, lebar belum final | Menolak versi rendah; persistensi produksi dan pengikatan versi/image perlu dirancang. |
| Register kebijakan | Register FPGA, lebar belum final | Daftar izin/ambang; lock mencegah perubahan host. |
| State replay | Register FPGA `last_sequence` | Monoton dalam sesi yang ditetapkan; persistensi aman saat reset belum dibuktikan. |
| Penghitung peristiwa | Register FPGA; contoh peristiwa memakai 32 bit | Monoton dalam satu periode; batas maksimum harus menolak secara aman atau memulai periode baru yang ditetapkan eksplisit. |
| Hash sebelumnya/terkini | Register FPGA, masing-masing 256 bit | Diperbarui setelah operasi rantai selesai; kontrak reset/genesis belum final. |
| Buffer peristiwa | M10K/BRAM, 16-64 peristiwa terbaru | Ring buffer beserta kendali/metadata hash; dikuras/disinkronkan HPS. Aturan buffer penuh/backpressure belum final. |
| Log jangka panjang | HPS/penyimpanan eksternal | Catatan dan hash diverifikasi terhadap anchor independen. |
| Checkpoint | Backend: ID perangkat, penghitung, hash 256 bit | Kepercayaan retensi/penerimaan diasumsikan pada MVP; snapshot harus atomik. |

## F. Batas Keamanan

Batas tepercaya FPGA meliputi logika inti, konfigurasi, dan masukan sensor setelah melewati antarmuka tepercaya. Transport perintah HPS dan log eksternal tidak boleh melewati pemeriksaan gerbang. Rantai SHA memberikan bukti perubahan relatif terhadap genesis/hash tepercaya. MVP tidak menyediakan enkripsi, forward-secure logging, atau penyimpanan yang mustahil diubah. Rantai tanpa kunci dapat dihitung ulang seluruhnya jika anchor tepercaya juga dapat diganti.

Pemotongan bagian akhir terdeteksi ketika bertentangan dengan checkpoint yang disimpan independen atau hash lokal tepercaya yang lebih baru. Peristiwa setelah checkpoint terakhir dapat hilang tanpa checkpoint itu membuktikan keberadaannya. Perlindungan pemalsuan/rollback checkpoint serta autentikasi transport backend belum diimplementasikan.

**Di luar MVP:** keamanan penuh backend, perlindungan DoS, serangan fisik invasif, side-channel/fault injection, pemalsuan sensor sebelum antarmuka, penyediaan kunci produksi, dan secure boot penuh dengan tanda tangan. MVP memverifikasi image aplikasi uji sebelum aktuator aktif. MVP belum membuktikan kode HPS mana yang benar-benar berjalan atau mencegah host mengganti aplikasi setelah pengukuran. Verifikasi tanda tangan firmware, penyediaan kunci aman, dan integrasi lebih dalam ke rantai boot merupakan pengembangan lanjutan.

## Target Sumber Daya dan Rencana Integrasi

Seluruh anggaran merupakan **target rekayasa — bukan hasil pengukuran**: <=4.000 ALM, <=5.000 FF, <=128 Kbit BRAM, 0 DSP, dan 50 MHz. Proposal mengutip kapasitas template kompetisi sebesar 110.000 LE / 41.910 ALM, BRAM 5.570 Kbit, dan 112 DSP. Angka tersebut merupakan kutipan sumber, bukan laporan penggunaan perangkat. Kapasitas dan kesesuaian aktual 5CSEBA6U23I7 perlu dikonfirmasi di Quartus.

Penggunaan bergantian menghindari replikasi SHA, tetapi menambah antrean. Kebijakan menggunakan komparator/FSM/register. Clock-enable SHA direncanakan aktif ketika ada permintaan. Angka daya memerlukan Quartus Power Analyzer dan asumsi aktivitas yang dijelaskan. [Rencana verifikasi](verification-plan.md) menetapkan bukti sebelum klaim implementasi dibuat.
