# ADR-003 — Registry Tool Eksplisit yang Terverifikasi

**Status:** Diterima

> *Pertanyaan yang dijawab ADR ini:* **Apa yang rusak diam-diam pas seseorang nambah tool tapi lupa satu titik wiring?**

## Masalah

Registrasi tool berbasis konvensyen gagal diam-diam. Bukti historisnya: **lima insiden terpisah** di mana satu kategori tool utuh hilang dari jangkauan agent hanya karena satu import package kelupaan. Nggak ada yang crash; tools-nya cuma diam-diam berhenti eksis buat model. Hilang-diam-diam adalah mode gagal terburuk yang bisa dimiliki agent — lo cuma sadar pas agent gagal di task yang seharusnya dia kuasai.

## Solusi

Registrasi **eksplisit di empat titik tetap**, dan **pemeriksa parity live** mengubah kontrak jadi tes:

1. Modul tool mendefinisikan fungsi dengan docstring yang menghadap model.
2. Definisi kategori mencantumkan nama-nama tool-nya.
3. Router mengetahui kategori itu.
4. `__init__` package meng-import modul untuk registrasi side-effect.

Pemeriksa parity membandingkan keempat lapisan dengan registry live saat runtime dan melaporkan: ghost (didefinisikan tapi tak ter-register), tool hilang, liar tak terkategori, dan duplikat. Run live terakhir: **ghost 0, missing 0, duplikat 0** di 425 tool.

## Konsekuensi

- "Kenapa agent nggak bisa make X?" jadi pertanyaan yang bisa dicek dengan satu perintah, bukan penggalian arkeologi.
- Lima kegagalan historis itu jadi mustahil terulang diam-diam — mereka akan menyalakan parity check di momen mereka terjadi.
- Tool baru butuh nyentuh empat titik, kelihatannya lebih berat — tapi disiplin ini menggantikan sesi debugging berulang yang masing-masing biayanya lebih besar dari seremoninya.
