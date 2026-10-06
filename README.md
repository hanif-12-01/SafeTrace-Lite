# SafeTrace Lite

**Inti keamanan siklus hidup berbasis FPGA yang ringan untuk sistem siber-fisik industri**

**"Percaya pada yang dijalankan. Percaya pada tindakan yang dilakukan. Percaya pada peristiwa yang tercatat."**

## Gambaran Proyek

SafeTrace Lite merupakan usulan inti kekayaan intelektual (*IP core*) keamanan berbasis FPGA yang menghubungkan integritas image aplikasi, otorisasi tindakan aktuator yang aman, dan riwayat keputusan yang dapat diverifikasi. Proyek ini ditujukan untuk **PERURI Chip Hackathon 2026**, dengan target **DE10-Nano / FPGA Cyclone V**. Ketiga lapisan keamanan menggunakan satu inti perangkat keras SHA-256 secara bersama.

Acuan utama desain adalah *SafeTrace Lite PERURI Proposal DOI Revisi*, proposal 11 halaman yang diberikan pemilik proyek. Repositori ini menerjemahkan desain tersebut menjadi spesifikasi teknis dan model referensi fungsional perangkat lunak. [Catatan sumber dan keputusan desain](docs/source-notes.md) memisahkan ketentuan proposal dari asumsi model.

## Latar Belakang dan Rumusan Masalah

Sistem siber-fisik industri menghubungkan perangkat lunak dan jaringan dengan sensor, aktuator, serta proses fisik. Modifikasi image aplikasi, pemalsuan atau pengulangan perintah, maupun perintah autentik yang melanggar batas keselamatan dapat memengaruhi proses tersebut. Log yang dapat diubah juga mengurangi keandalan bukti insiden.

SafeTrace Lite mengusulkan titik pemeriksaan kepercayaan di perangkat keras yang menghubungkan image yang diterima, tindakan yang diizinkan, dan keputusan yang dicatat. Kontribusinya berada pada integrasi siklus hidup serta penggunaan sumber daya bersama, tanpa mengklaim primitif kriptografi baru atau sistem pertama di dunia.

## Solusi yang Diusulkan

HPS ARM menjalankan antarmuka pengguna dan menjadi jalur pengiriman image uji, perintah, serta log. Keputusan keamanan dilakukan pada FPGA. Verifikasi awal menetapkan `SYSTEM_TRUSTED`; setiap perintah selanjutnya harus memenuhi autentikasi, kebaruan nomor urut, dan kebijakan keselamatan deterministik. Setiap keputusan ALLOW/BLOCK dicatat sebagai peristiwa audit. Backend menyimpan checkpoint berupa penghitung dan hash untuk membantu mendeteksi riwayat yang tidak konsisten atau terpotong.

## Tiga Lapisan Keamanan

| Lapisan | Pemeriksaan dan keluaran | Batas MVP |
| --- | --- | --- |
| **Boot Integrity Gate — Gerbang Integritas Awal** | Digest SHA-256 image sesuai acuan tepercaya; versi keamanan memenuhi batas minimum | Memverifikasi image aplikasi uji sebelum `ACTUATOR_ENABLE`. MVP tidak menggantikan secure boot bawaan board atau menyediakan verifikasi tanda tangan firmware untuk produksi. |
| **Runtime Action Guard — Pengaman Tindakan Saat Operasi** | HMAC-SHA256, nomor urut yang meningkat, kebijakan keselamatan perangkat keras, dan keputusan ALLOW/BLOCK | Perintah yang autentik tetap harus memenuhi batas nilai dan kondisi sensor yang aman. |
| **TrustLog — Jejak Audit Terverifikasi** | Penghitung peristiwa, rantai hash SHA-256, dan checkpoint hash terakhir | Perubahan dibuktikan melalui verifikasi. Data tetap dapat dimodifikasi; penghapusan bagian akhir yang belum tercakup checkpoint tidak selalu terdeteksi. |

$$
\mathrm{ALLOW} = \mathrm{SYSTEM\_TRUSTED} \land \mathrm{HMAC\_VALID} \land \mathrm{FRESH\_SEQUENCE} \land \mathrm{POLICY\_VALID}
$$

ALLOW berarti perintah diizinkan; BLOCK berarti perintah diblokir.

## Diagram Arsitektur Sistem

![Usulan arsitektur perangkat keras SafeTrace Lite](docs/block-diagram.png)

Panah utuh menunjukkan aliran data, konfigurasi, atau keputusan. Panah putus-putus menunjukkan permintaan dan hasil layanan SHA. BLOCK mempertahankan keluaran tidak aktif; kedua jenis keputusan masuk ke TrustLog. Batas FPGA mencakup seluruh logika keputusan. Diagram merupakan spesifikasi desain. [Sumber Mermaid yang dapat disunting](docs/block-diagram.mmd), [rincian arsitektur](docs/architecture.md), dan [skrip pembentuk PNG](tools/render_diagram.py) tersedia.

## Target Perangkat Keras dan Teknologi

Target yang direncanakan adalah DE10-Nano, Cyclone V SE **5CSEBA6U23I7**, HPS ARM, Avalon-MM melalui lightweight HPS-to-FPGA bridge, Platform Designer, serta Verilog/SystemVerilog. Sensor demonstrasi menggunakan sakelar/ADC/GPIO; keluaran demonstrasi berupa LED/PWM atau motor bertegangan rendah melalui rangkaian driver.

Angka berikut merupakan **target rekayasa — bukan hasil pengukuran**, berdasarkan proposal halaman 7-9:

| Metrik | Target awal |
| --- | --- |
| Frekuensi clock FPGA | 50 MHz; harus dibuktikan melalui analisis timing Quartus |
| Logika dan register | <=4.000 ALM / <=5.000 FF |
| BRAM dan DSP | <=128 Kbit / 0 blok DSP |
| Latensi satu blok SHA-256 | <5 mikrodetik pada 50 MHz |
| Latensi HMAC perintah pendek | <25 mikrodetik pada 50 MHz |
| Evaluasi kebijakan | <=5 siklus setelah pemeriksaan autentikasi dan nomor urut |
| Pembaruan TrustLog | Satu blok SHA untuk peristiwa 128 bit dan hash sebelumnya 256 bit, ditambah kendali |

Hasil RTL, sintesis, timing, daya, dan pengujian board belum tersedia. Waktu tunggu akibat penggunaan inti bersama perlu diperhitungkan dalam pengukuran latensi menyeluruh.

## Keamanan Sejak Tahap Perancangan

Gerbang keluaran dirancang dengan prinsip *default-deny*: BLOCK saat reset, boot belum tepercaya, atau terjadi kesalahan. Digest tepercaya, kunci HMAC, versi minimum, dan konfigurasi kebijakan berada dalam batas kepercayaan FPGA. Penulisan oleh host harus ditolak setelah konfigurasi dikunci, dan kunci tidak boleh terbaca oleh host. Pemeriksaan nomor urut mendahului evaluasi kebijakan. ALLOW maupun BLOCK sama-sama dicatat. Rantai hash memberikan bukti integritas; enkripsi dan kerahasiaan tidak termasuk MVP.

## Model Ancaman dan Batasan

MVP mencakup modifikasi image uji, versi di bawah minimum, HMAC tidak valid, replay dalam sesi yang sama, perintah atau kondisi sensor yang tidak aman, perubahan log, dan pemotongan log yang bertentangan dengan checkpoint tepercaya.

Di luar cakupan: serangan fisik invasif, side-channel, fault injection/ekstraksi kunci, pemalsuan sebelum antarmuka sensor tepercaya, ketersediaan jaringan/DoS, keamanan penuh backend, dan penyediaan kunci untuk produksi. Anchor backend diasumsikan tepercaya dan disimpan secara independen. Persistensi saat reset, pengikatan autentik versi dengan image, penerimaan checkpoint, dan penanganan buffer penuh masih memerlukan keputusan protokol/RTL; lihat [catatan sumber](docs/source-notes.md). Rantai hash tanpa kunci tidak mencegah penulisan ulang seluruh riwayat jika penyerang juga dapat mengganti anchor tepercayanya.

## Struktur Repositori

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

## Strategi Verifikasi

[Rencana verifikasi](docs/verification-plan.md) memetakan bagian 3.2 proposal ke skenario T1-T12. Jalankan pengujian model dengan Python 3.10+ dan pustaka standar dari direktori utama repositori:

```sh
python -m unittest discover -s tests -v
python -m simulation.demo
python tools/validate_repository.py
```

Model hanya memeriksa keputusan fungsional dan verifikasi audit. Rencana Verilator/ModelSim dan cocotb harus memverifikasi antarmuka RTL, vektor SHA/HMAC dengan hasil acuan yang diketahui, kepemilikan inti oleh penjadwal, waktu per siklus, dan reset di tengah transaksi. Quartus dan SignalTap akan menyediakan bukti sintesis, timing, serta keluaran fisik. [Peta jalan simulasi](simulation/README.md) dan [batas cakupan pengujian](tests/README.md) menjelaskan perbedaannya.

## Peta Jalan Pengembangan

| Tahap | Luaran | Status |
| --- | --- | --- |
| Penyiapan repositori | Arsitektur, diagram, spesifikasi verifikasi, daftar pustaka DOI | Tersedia |
| Referensi fungsional | Model Python untuk boot/HMAC/replay/kebijakan/rantai hash/checkpoint | Tersedia; perangkat lunak saja |
| Bootcamp hari 1 | Integrasi SHA, antarmuka register, Boot Integrity Gate, vektor SHA, kerangka Action Guard | Direncanakan |
| Bootcamp hari 2 | HMAC/replay/kebijakan, peristiwa tetap, TrustLog, pengujian RTL menyeluruh, laporan Quartus | Direncanakan |
| Bootcamp hari 3 | Bridge HPS, SignalTap, demo LED/PWM/motor, skenario serangan, video dan metrik terukur | Direncanakan |
| Pengembangan lanjutan | PUF/penyediaan kunci aman, tanda tangan ECC firmware, tabel kebijakan yang dikunci, sensor dan uji gangguan tambahan, eksplorasi ASIC, Merkle/history tree | Di luar MVP |

Jadwal bootcamp tiga hari merupakan rencana dalam proposal. Yosys/OpenROAD dengan SkyWater 130 nm merupakan jalur eksplorasi ASIC opsional.

## Referensi Ilmiah

[Daftar pustaka DOI](docs/references.md) mempertahankan referensi [1]-[16] dari proposal: keamanan ICPS [1]-[4], secure bootstrap/akar kepercayaan [5]-[6], penjaminan keselamatan saat operasi dan perangkat keras tepercaya [7]-[8], pencatatan log aman [9]-[10], HMAC [11], FPGA SHA-256 [12]-[13], serta standar teknis NIST ber-DOI [14]-[16]. Dokumen board dan kompetisi dipisahkan sebagai spesifikasi serta persyaratan.

## Status Proyek

**Usulan Arsitektur / Praimplementasi**

Dokumentasi dan model referensi fungsional perangkat lunak telah tersedia. RTL FPGA, integrasi cocotb, proyek/bitstream Quartus, sintesis, pengujian perangkat keras, dan benchmark masih direncanakan. Hasil pengujian Python tidak membuktikan kebenaran FPGA, timing, penggunaan sumber daya, atau ketahanan terhadap serangan fisik.
