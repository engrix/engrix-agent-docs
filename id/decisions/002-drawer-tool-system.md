# ADR-002 — Sistem Laci untuk Ratusan Tool

**Status:** Diterima

> *Pertanyaan yang dijawab ADR ini:* **Bagaimana ratusan tool tetap terlihat tanpa menenggelamkan tiap request?**

## Masalah

> *Bagaimana caranya agent bisa memakai ratusan tools tanpa kebingungan — dan pemilihannya tepat?*

Di 425 tool, dua desain yang paling jelas sama-sama gagal:

- **Semua schema selalu di prompt** — biaya token meledak, nama tool yang mirip saling melebur, kualitas pemilihan turun. Model tenggelam.
- **Similarity search atas deskripsi tool** — layer retrieval *menebak* tool mana yang mungkin relevan. Tebakan salahnya susah di-debug, dan model tidak pernah lihat katalog lengkap, jadi ia bahkan tidak tahu harus minta apa.

## Solusi

**Taksonomi laci tiga lapis** yang dimodelkan dari perpustakaan: katalog lengkap selalu terdaftar (nama + jumlah + contoh trigger), tapi schema penuh dimuat hanya pas laci dibuka.

1. **17 tool always-on** — planning, search, manajemen-diri; dibutuhkan tiap request.
2. **22 kategori** — dibuka eksplisit oleh model lewat panggilan router rule-based. Membuka = memuat schema untuk sisa sesi. Shortcut satu keluarga membuka lima drawer kode sekaligus.
3. **40 subdomain** — subset kategori yang besar, agar "hanya butuh devtools" tidak menyeret semua 37 tool browser.

Pemilihan tetap presisi karena:

- **Routing-nya eksplisit** — model menyebut nama laci yang ia mau; router men-resolve persis itu. Tidak ada tebakan similarity di mana pun.
- **Kategori dikelompokkan berdasarkan ekosistem pemakaian nyata** (GitHub+Gist bareng; git lokal vs GitHub remote dipisah keras), dan keluarga yang besar dipecah granular agar kerja kecil tidak menanggung payload gede.
- **Peluruhan hot/cold** — kategori yang tidak dipakai kehilangan deskripsinya dari menu statis setelah 3 task idle; nama dan contoh tetap ada agar model selalu bisa membukanya.

## Konsekuensi

- Payload iterasi-0 tetap kecil berapa pun besar inventaris tool-nya tumbuh.
- Menambah tool tidak pernah menurunkan prompt default — hanya laci tempat ia tinggal yang tumbuh.
- Tradeoff-nya satu panggilan router ekstra pas butuh laci; perilaku yang teramati: model membuka drawer dengan rajin dan tepat kalau contoh trigger-nya ditulis dengan baik.
