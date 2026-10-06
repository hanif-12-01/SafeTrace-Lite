# Cakupan dan Batas Pengujian

Jalankan dari direktori utama repositori dengan Python 3.10+:

```sh
python -m unittest discover -s tests -v
```

`test_reference_model.py` mencakup T1-T11 secara fungsional dan bagian kondisi aman T12. Pengujian tambahan memeriksa byte peristiwa, autentikasi field perintah, pencegahan pembaruan nomor urut oleh HMAC palsu, ID tidak dikenal, default-deny, penulisan ulang riwayat terjangkar, kelanjutan checkpoint/ID perangkat, batas deteksi pemotongan tanpa anchor, nomor urut maksimum, dan penghitung peristiwa yang habis.

Vektor dengan hasil acuan yang diketahui meliputi SHA-256 untuk `abc` dan contoh HMAC-SHA256. Byte hasil yang diharapkan ditetapkan secara independen dari fungsi yang diuji. Pemeriksaan ini memvalidasi dasar primitif/pengodean perangkat lunak; hasilnya tidak membuktikan kebenaran inti SHA pada RTL.

| Cakupan | Bukti saat ini |
| --- | --- |
| T1-T3 | Keputusan digest/versi model dan keluaran tidak aktif |
| T4-T9 | Autentikasi/nomor baru/kebijakan, alasan, state replay, pembaruan peristiwa/hash |
| T10 | Perubahan catatan, pertukaran urutan, dan penolakan riwayat terjangkar yang dihitung ulang |
| T11 | Pemotongan 105→104, ketidaksesuaian hash/ID checkpoint, dan kelanjutan yang sah |
| T12 | Reset di antara pemanggilan atomik membersihkan state aman dan mencegah kepercayaan lama; reset di tengah transaksi RTL belum diuji |

Keluaran dari pengujian yang benar-benar dijalankan menjadi sumber hasil lulus/gagal. Waveform, laporan sintesis, benchmark timing, serta hasil perangkat keras belum tersedia. Pengujian fungsional dipisahkan dari validasi dokumen; [validator repositori](../tools/validate_repository.py) memeriksa tautan, kelengkapan, DOI, dan struktur PNG.

Pengujian cocotb ditambahkan ketika RTL nyata tersedia. Cakupannya harus meliputi persaingan layanan SHA, register terkunci, handshake/backpressure, batas penghitung, pesan tidak lengkap, dan reset pada setiap tahap transaksi. Ikuti [rencana verifikasi](../docs/verification-plan.md); pengujian perangkat lunak ini belum memenuhi seluruh penerimaan perangkat keras.
