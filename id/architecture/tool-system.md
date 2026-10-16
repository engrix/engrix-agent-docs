# Sistem Tool

Fitur paling menentukan dari Engrix Agent: **425 tool ter-register di 22 kategori**. Aritmatikanya tutup persis: `425 ter-register = 407 terkategori + 17 always-on + 1 meta-tool` — `open_tool_category`, si pembuka laci itu sendiri, sengaja di luar kategori. Checker yang sama juga melaporkan dua lint penamaan non-blocking (70 pasangan nama mirip — banyak yang memang disengaja, misal `email_*` vs `gmail_*` laci yang berbeda — dan satu nama di atas 40 char), direview, bukan disembunyikan. Diukur lewat registry parity checker, 16-10-2026, terhadap commit `b1a7a71`.

## Pertanyaannya

> *Bagaimana caranya agent bisa memakai ratusan tools tanpa kebingungan — dan pemilihannya tepat?*

Pendekatan naif gagal di skala ini. Memasukkan 425 schema tool ke setiap request membuat prompt membengkak dan model tenggelam: nama yang mirip saling melebur, kualitas pemilihan turun, biaya token meledak. Menyembunyikan tool dari model sama sekali juga tidak bisa — ia tidak tahu apa yang tersedia.

## Solusinya: sistem laci tiga lapis

Tools diorganisir seperti perpustakaan sungguhan — katalognya selalu terlihat, tapi hanya rak yang dibutuhkan yang dibawa:

| Lapis | Apa itu | Jumlah |
|---|---|---|
| **Always-on** | Tool planning, search, dan manajemen-diri yang tiap request butuhin | 17 |
| **Kategori** | Laci-lacinya — dibuka eksplisit pas task butuh | 22 (+1 shortcut satu keluarga) |
| **Subdomain** | Laci di dalam laci — subset dari kategori besar | 40 |

Pemandangan tiap request tetap datar seberapapun dalamnya inventaris:

```
tiap request ──▶ [ always-on: 17 tool ]
                 [ menu: 22 nama kategori + jumlah + contoh trigger ]  ◀── kecil, statis
                         │
       model memilih by intent, satu call:  open_tool_category("github")
                         │
                         ▼
       sisa sesi ──▶ [ drawer github: 83 schema penuh ]  ◀── dimuat sekali
                     [ opsi subdomain: repo_code (16) · pr (3) · … ]
```

Saat task mulai, model hanya lihat menu ringkas: nama kategori, jumlah tool, dan contoh trigger. Membuka kategori (`open_tool_category`) memuat schema penuh laci itu plus instruksi pemakaian detail **untuk sisa sesi** — tidak perlu dibuka ulang. Shortcut satu keluarga (`code_workspace`) membuka lima drawer kode sekaligus buat sesi engineering berat.

## Disiplin pemilihan

Tiga mekanisme yang membuat pemilihan tetap presisi:

1. **Routing eksplisit, bukan similarity search.** Model *memilih* kategori lewat namanya, di-resolve router rule-based. Tidak ada embedding retrieval yang menebak "tool mana yang mungkin relevan" — model menalar intent, router mengeksekusi persis permintaannya.
2. **Pengelompokan berdasarkan pemakaian nyata, bukan nama.** Kategori mencerminkan cara kerja yang sesungguhnya: GitHub + Gist satu drawer (ekosistem sama), sementara git *lokal* dan GitHub *remote* sengaja dipisah (domain berbeda, tidak pernah dicampur). Keluarga `code_exec` yang besar dipecah menjadi enam drawer granular agar "hanya ingin menjalankan pytest" tidak sekalian menyeret terminal + kernel + LSP + operasi file.
3. **Peluruhan hot/cold.** Kategori yang tidak dipakai 3 task terakhir kehilangan deskripsi penuhnya dari menu statis (nama + contoh tetap ada) — payload always-on tetap kecil, dan deskripsi penuh balik otomatis pas kategori jadi hot lagi.

## Kenapa tools-nya bisa dipercaya

Registry-nya kontrak yang diverifikasi, bukan konvensyen. Pemeriksa parity membandingkan definisi kategori dengan yang benar-benar ter-register saat import, dan **hard-fail** pada ghost (didefinisikan tapi tak ter-register), missing tool, drift always-on, dan duplikat — ia jalan sebagai gate pre-commit tiap ada perubahan `tools/`, sengaja berupa perintah yang dijalankan manual, bukan daemon latar (header checker-nya sendiri mendokumentasikan aturan itu). Temuan lint penamaan dilaporkan sebagai warning, tidak pernah dipendam diam-diam. Tiap penambahan lewat protokol registrasi empat titik yang eksplisit — lihat [keputusan registry](../decisions/003-explicit-tool-registry.md).

Lanjut ke: [Memori Berlapis](memory.md) — bagaimana agent tidak pernah kehilangan benang merah.
