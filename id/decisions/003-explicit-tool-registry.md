# ADR-003 — Registry Tool yang Eksplisit dan Terverifikasi

**Status:** Diterima

> *Pertanyaan yang dijawab ADR ini:* **Apa yang rusak diam-diam saat seseorang menambah tool dan lupa satu titik wiring?**

## Masalah

Registrasi tool berbasis konvensi gagal tanpa suara. Bukti historisnya: **lima insiden terpisah** di mana satu kategori tool hilang dari jangkauan agent karena satu import paket terlupa. Tidak ada yang crash; tool-nya cuma diam-diam berhenti ada bagi model. Hilang tanpa suara adalah mode kegagalan terburuk sebuah agent — lo baru sadar saat agent gagal di task yang seharusnya gampang.

## Solusi

Registrasi bersifat **eksplisit di empat titik tetap**, dan **checker paritas hidup** mengubah kontraknya jadi test:

1. Modul tool mendefinisikan fungsi dengan docstring berorientasi model.
2. Definisi kategori mencantumkan nama tool-nya.
3. Router mengenal kategorinya.
4. `__init__` paket mengimpor modul untuk registrasi efek samping.

Checker paritas (`scripts/check_registry_sync.py`) membandingkan keempat lapis terhadap registry hidup saat runtime dan melaporkan: ghost (didefinisikan tapi tidak ter-register), tool hilang, stray tanpa kategori, dan duplikat. `scripts/check_contracts.py` memperluas disiplin yang sama ke literal kategori, subdomain, dan set always-on, dan mengirim self-test yang membuktikan gate-nya memang mampu gagal — gate yang belum pernah terlihat gagal bukanlah gate.

## Konsekuensi

- "Kenapa agent tidak bisa memakai X?" jadi pertanyaan yang bisa dicek dengan satu perintah alih-alih penggalian arkeologi.
- Lima kegagalan historis itu secara struktural tidak bisa terulang diam-diam — mereka akan langsung menyalakan cek paritas saat terjadi.
- Tool baru menuntut menyentuh empat titik, yang terdengar lebih berat — tapi disiplin ini menggantikan sesi debugging berulang yang masing-masing lebih mahal daripada upacaranya.

## Bagian yang butuh waktu lebih lama untuk dipelajari

Protokol empat titik menangkap titik wiring yang *terlupa*. Ia tidak menangkap **gate yang mengukur nol**. Dua gate di repo ini sempat berbulan-bulan melaporkan sukses sambil memindai nol file: satu karena flag quiet ganda menekan baris ringkasan yang sedang ia parsing, satu lagi karena pola path-nya tidak pernah cocok dengan tata letak yang benar-benar dipakai repo.

Pelajaran itu berlaku di luar proyek ini: *"tidak ada temuan" dan "tidak memindai apa pun" identik kalau satu-satunya output adalah exit code.* Kedua gate sekarang memperlakukan pemindaian kosong sebagai kegagalan, dan aturannya ditulis sebagai known issue dengan perintah verifikasinya sendiri.
