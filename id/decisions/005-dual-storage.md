# ADR-005 — Dua Engine Storage, Masing-masing untuk yang Dia Kuasai

**Status:** Diterima

> *Pertanyaan yang dijawab ADR ini:* **Kenapa bawa dua database padahal satu secara teknis bisa ngerjain dua-duanya?**

## Masalah

Agent butuh dua jenis memori yang tidak kompatibel: **state terstruktur relasional** (fakta sesi, posisi task, catatan verifikasi) yang harus konsisten dan bisa di-query, dan **konten semantik** (dokumen, digest percakapan, poin knowledge) yang harus ditemukan berdasarkan makna, bukan kecocokan persis. Memaksa salah satunya ke engine yang salah bikin dua-duanya lebih susah.

## Solusi

**SQLite (mode WAL)** memegang state terstruktur: satu koneksi, write-lock cursor terlindungi, schema versioning dengan migrasi. **Qdrant** memegang recall semantik, dengan client dual-mode — embedded buat satu instance, server mode pas instance jalan paralel. Layer storage (`storage/`) pegang mekanik; layer memory (`memory/`) pegang makna; kode domain menyentuh storage hanya lewat batas itu.

## Konsekuensi

- Deployment tanpa dependency: seluruh agent jalan dari satu folder — nggak butuh database server buat state terstruktur.
- Instance paralel jadi aman dengan membalik satu setelan (embedded → server vector mode) daripada re-arsitektur.
- Evolusi schema dikendalikan migrasi, bukan `ALTER TABLE` tersebar di kode — memori agent hidup lebih lama dari versi mana pun.
