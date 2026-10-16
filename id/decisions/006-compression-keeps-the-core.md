# ADR-006 — Kompresi yang Menjaga Inti (Desain Memori)

**Status:** Diterima

> *Pertanyaan yang dijawab ADR ini:* **Gimana kalau kompresi justru menghapus detail yang dibutuhkan task nanti?**

## Masalah

Kebutuhan awalnya blak-blakan:

> *"Asisten yang bisa semuanya, bisa di mana pun, dan nggak pernah lupa konteks."*

Riwayat chat saja gagal persis di sini. Dia membengkak sampai model kehilangan awal di tengah, atau dipotong dan agent lupa task-nya sendiri. Dan "lupa" itu bukan satu masalah — minimal empat: lupa fakta, lupa langkah sekarang, lupa sesi lampau, lupa apa yang dibahas percakapan lain.

## Solusi

Perlakukan "nggak pernah lupa" sebagai **store berlapis**, masing-masing memegang satu jenis kelupaan — semua dirancang di sekitar prinsip yang sama: *kompres agresif, tapi inti selalu ada.*

| Jenis kelupaan | Store |
|---|---|
| Fakta yang disebut dalam sesi | Ekstraksi fakta mekanis (nol halusinasi, difilter stopword) |
| Lagi di mana dalam task | Blok posisi task di-inject di **setiap** giliran model |
| Yang terjadi di sesi lampau | Episode index yang di-format on demand |
| Yang dibahas percakapan lain | Index topik berupa pointer; isinya diambil dari vector store saat perlu |

Detail penopang: output tool yang panjang di riwayat **dikompaksi, bukan dibuang** — layer yang sama yang menambah pesan memegang kompaksi, jadi pandangan model atas riwayatnya sendiri tetap koheren. Di dalam satu task room, makin dalam chat berarti *makin terkompres, inti sama* — konteks room makin ramping seiring waktu, bukan makin bengkak.

## Konsekuensi

- Agent di jam keempat tetap membawa kerangka task-nya di depan mata setiap giliran.
- "Memori" halusinatif tersupresi struktural: fakta masuk hanya lewat ekstraksi mekanis, tidak pernah lewat model meringkas dirinya sendiri bebas.
- Pengalaman lintas-sesi terakumulasi: task baru mulai lebih pintar karena ringkasan task lampau hanya satu retrieval jauhnya.
