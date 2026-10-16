# ADR-002 — Sistem Laci untuk Ratusan Tool

**Status:** Diterima

## Masalah

> *Gimana caranya agent bisa make ratusan tools tanpa kebingungan — dan pemilihannya tepat?*

Di 425 tool, dua desain yang paling jelas sama-sama gagal:

- **Semua schema selalu di prompt** — biaya token meledak, nama tool yang mirip saling melebur, kualitas pemilihan turun. Model tenggelam.
- **Similarity search atas deskripsi tool** — layer retrieval *menebak* tool mana yang mungkin relevan. Tebakan salahnya susah di-debug, dan model nggak pernah lihat katalog lengkap, jadi dia bahkan nggak tahu harus minta apa.

## Solusi

**Taksonomi laci tiga lapis** yang dimodelkan dari perpustakaan: katalog lengkap selalu terdaftar (nama + jumlah + contoh trigger), tapi schema penuh dimuat hanya pas laci dibuka.

1. **17 tool always-on** — planning, search, manajemen-diri; dibutuhkan tiap request.
2. **22 kategori** — dibuka eksplisit oleh model lewat panggilan router rule-based. Membuka = memuat schema untuk sisa sesi. Shortcut satu keluarga membuka lima drawer kode sekaligus.
3. **40 subdomain** — subset kategori yang kegedean, jadi "gua cuma butuh devtools" nggak nyeret semua 37 tool browser.

Pemilihan tetap presisi karena:

- **Routing-nya eksplisit** — model menyebut nama laci yang dia mau; router men-resolve persis itu. Nggak ada tebakan similarity di mana pun.
- **Kategori dikelompokkan berdasarkan ekosistem pemakaian nyata** (GitHub+Gist bareng; git lokal vs GitHub remote dipisah keras), dan keluarga yang kegedean dipecah granular biar kerja kecil nggak nanggung payload gede.
- **Peluruhan hot/cold** — kategori yang nggak dipakai kehilangan deskripsinya dari menu statis setelah 3 task idle; nama dan contoh tetap ada biar model selalu bisa membukanya.

## Konsekuensi

- Payload iterasi-0 tetap kecil berapa pun besar inventaris tool-nya tumbuh.
- Menambah tool nggak pernah menurunkan prompt default — cuma laci tempat dia tinggal yang tumbuh.
- Tradeoff-nya satu panggilan router ekstra pas butuh laci; perilaku yang teramati: model membuka drawer dengan rajin dan tepat kalau contoh trigger-nya ditulis dengan baik.
