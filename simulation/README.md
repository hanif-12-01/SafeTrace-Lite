# Model Referensi Fungsional Perangkat Lunak

Direktori ini berisi **model referensi fungsional perangkat lunak** yang dapat dijalankan dengan Python 3.10+, menggunakan `hashlib`, `hmac`, `struct`, dan dataclasses. Model menjadi spesifikasi perilaku untuk sebagian fungsi proposal. Model ini bukan emulator FPGA atau hasil verifikasi RTL.

Jalankan dari direktori utama repositori:

```sh
python -m unittest discover -s tests -v
python -m simulation.demo
```

Demo menampilkan boot valid, perintah aman ALLOW, perintah tidak aman/replay BLOCK, log bersih yang sesuai checkpoint, dan penolakan log yang diubah. Kunci contoh dibuat di memori dan memang bersifat publik untuk pengujian; tidak ada credential perangkat nyata.

## Fungsi yang Tersedia dan Peta Jalan Integrasi

| Tahap | Status perangkat lunak | Rencana integrasi perangkat keras |
| --- | --- | --- |
| 1. Referensi fungsional Python | `reference_model.py` | Menjadi pembanding cocotb setelah format RTL ditetapkan. |
| 2. Integritas boot | Perbandingan digest/versi minimum dan kepercayaan default-deny | Streaming/padding image, inti SHA bersama, konfigurasi terlindungi. |
| 3. Autentikasi HMAC | Tag SHA-256 lengkap atas ID/nilai/nomor urut dengan `compare_digest` | Hash bagian dalam/luar dan perbandingan seluruh tag pada inti bersama. |
| 4. Deteksi replay | Nomor u32 meningkat ketat dalam satu periode reset | Tetapkan sesi/persistensi dan pembaruan state atomik. |
| 5. Kebijakan keselamatan | ID 1 untuk kecepatan; batas kecepatan/suhu inklusif | Komparator/FSM dan pengambilan sensor yang konsisten. |
| 6. Rantai SHA-256 | Peristiwa 16 byte, genesis terkait boot, dan penghitung | Format tetap, penjadwal SHA, dan M10K/BRAM. |
| 7. Deteksi perubahan | Pemeriksaan peristiwa/hash dan checkpoint independen | Jalur verifikasi FPGA dan alur checkpoint HPS/backend. |
| 8. Integrasi RTL | Direncanakan | Verilator/ModelSim, cocotb, wrapper Avalon-MM, Quartus, dan SignalTap. |

## Kontrak Model

`SafeTraceModel` menerima konfigurasi tetap: digest image tepercaya 32 byte, kunci demo 32 byte, versi minimum, dan batas kebijakan. `boot(image, version)` dijalankan satu kali per periode reset dan tidak langsung mengaktifkan aktuator. `process(command, tag, temperature, timestamp)` mengevaluasi satu transaksi atomik, mengembalikan `Decision`, lalu menambahkan peristiwa setelah boot selesai. Perintah sebelum boot ditolak dan tidak membentuk periode audit tepercaya. ALLOW maupun BLOCK setelah boot selesai dicatat.

Payload perintah menggunakan `>BHI`: ID u8, nilai u16, dan nomor urut u32. Tag mengautentikasi **seluruh** byte payload. Nomor urut awal adalah nol, sehingga nomor pertama yang diterima minimal satu. Nomor baru yang autentik dipakai sebelum evaluasi kebijakan, termasuk jika tindakan ditolak. Autentikasi gagal tidak memperbarui nomor; ID tidak dikenal ditolak. Penghitung yang habis menonaktifkan keluaran dan menghasilkan kesalahan eksplisit, tanpa berputar ke nol atau mengizinkan tindakan yang tidak tercatat.

Format peristiwa adalah `>IIBHHBH`: penghitung:u32, timestamp_low:u32, command_id:u8, nilai:u16, sensor/suhu:u16, keputusan+alasan:u8, dan versi:u16. Ukuran 16 byte mengikuti contoh proposal. Enumerasi alasan dan big-endian merupakan asumsi model. Genesis model menghitung hash label domain, ID perangkat, digest image terukur, versi masukan, dan hasil boot. Protokol genesis perangkat keras belum final.

`checkpoint()` menghasilkan ID perangkat, penghitung, dan hash terakhir. `verify_log(records, genesis, device_id, checkpoint)` menghitung ulang setiap catatan, memeriksa urutan penghitung, dan membandingkan bagian rantai pada checkpoint yang disimpan. Kelanjutan log yang sah diterima; log lebih pendek atau hash/ID terjangkar yang salah ditolak. `verify_stored_log` membandingkan dengan hash model sendiri dan mengunci `tamper_flag` saat penolakan. Genesis/checkpoint harus diperoleh dari sumber tepercaya yang independen dari file log yang mungkin telah diubah.

`reset()` menonaktifkan aktuasi dan membersihkan kepercayaan runtime, nomor urut, penghitung, serta log di memori; konfigurasi tetap dipertahankan. Reset ini tidak menyediakan anti-replay persisten, reset perangkat keras di tengah siklus, atau penghapusan aman rahasia dari memori Python. Simpan checkpoint secara independen sebelum reset untuk memeriksa riwayat. Boot berulang dapat menghasilkan genesis identik; kebaruan sesi lintas reset belum ditetapkan.

Model memakai list tanpa batas kapasitas, timestamp masukan, dan pemanggilan atomik. Penjadwalan SHA, BRAM penuh, durasi PWM, penyelesaian fisik aktuator, penguncian register, clock asinkron, penyediaan kunci produksi, dan jaringan backend tidak dimodelkan. Lihat [catatan sumber](../docs/source-notes.md) dan [rencana verifikasi](../docs/verification-plan.md) untuk pekerjaan lanjutan.
