# ADR-002 — Sistem Laci untuk Ratusan Tool

**Status:** Diterima

> *Pertanyaan yang dijawab ADR ini:* **Bagaimana ratusan tool tetap terlihat tanpa menenggelamkan setiap request?**

## Masalah

Di skala ini, dua desain yang paling jelas sama-sama gagal:

- **Semua schema selalu di prompt** — biaya token meledak, nama tool yang mirip saling melebur, kualitas pemilihan turun. Model tenggelam.
- **Pencarian kemiripan atas deskripsi tool** — layer retrieval *menebak* tool mana yang mungkin relevan. Tebakan salah dengan cara yang sulit di-debug, dan model tidak pernah melihat katalog penuh, jadi ia bahkan tidak tahu apa yang bisa diminta.

Masalahnya bukan "tool kebanyakan". Masalahnya: **tampilan per-request model harus tetap terbatas sementara inventarisnya terus tumbuh**.

## Solusi

**Taksonomi laci tiga lapis** yang meniru perpustakaan: katalog penuh selalu terdaftar (nama + jumlah + contoh trigger), tapi schema penuh hanya dimuat saat laci dibuka.

1. **Tool always-on** — planning, search, manajemen-diri; dibutuhkan setiap request.
2. **Kategori** — dibuka eksplisit oleh model lewat panggilan router berbasis aturan. Membuka memuat schema untuk sisa sesi. Shortcut keluarga membuka lima laci kode sekaligus.
3. **Subdomain** — subset dari kategori kebesaran, jadi "gue cuma butuh devtools" tidak menyeret seluruh laci browser.

Jumlah persisnya sengaja **tidak ditulis di sini**. Angkanya tinggal di kode dan di-assert oleh `scripts/verify_docs_claims.py`, yang menggagalkan dokumen saat sebuah angka melenceng. Catatan keputusan seharusnya menyatakan keputusannya; jumlah inventaris adalah pengukuran, dan pengukuran milik gate.

Pemilihan tetap presisi karena:

- **Routing eksplisit** — model menyebut laci yang diinginkannya; router me-resolve persis itu. Tidak ada tebakan kemiripan di mana pun.
- **Kategori dikelompokkan berdasarkan ekosistem pemakaian nyata** (GitHub+Gist bersama; git lokal vs GitHub remote tegas terpisah), dan keluarga kebesaran dipecah granular supaya pekerjaan kecil tidak membawa payload besar.
- **Peredupan hot/cold** — kategori yang tidak dipakai kehilangan deskripsinya dari menu statis setelah 3 task idle; nama dan contoh tetap ada supaya model selalu bisa membukanya.

## Konsekuensi

- Payload iterasi-0 tetap kecil seberapa besar pun inventaris tool tumbuh.
- Menambah tool tidak pernah menurunkan kualitas prompt default — hanya laci tempatnya yang membesar.
- Tukarannya satu panggilan router tambahan saat laci dibutuhkan; perilaku teramati menunjukkan model membuka laci dengan rajin dan benar kalau contoh trigger-nya ditulis bagus.
- Biaya orde kedua nyata dan layak disebut: sistem laci hanya bekerja kalau *menu*-nya jujur. Kategori yang contoh trigger-nya kabur membuat model membuka laci yang salah, dan kegagalannya tampak seperti kesalahan penalaran alih-alih kesalahan katalog.
