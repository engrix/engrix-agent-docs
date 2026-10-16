# Sistem Tool

Fitur paling menentukan dari Engrix Agent: **425 tool ter-register di 22 kategori** (cek registry live: `425 tool registered | 22 kategori | 407 tool terkategori | 17 always-on`, ghost 0, missing 0, duplikat 0).

## Pertanyaan kritisnya

> *Gimana caranya agent bisa make ratusan tools tanpa kebingungan — dan pemilihannya tepat?*

Pendekatan naif gagal di skala ini. Menjejalkan 425 schema tool ke setiap request bikin prompt membengkak dan model tenggelam: nama yang mirip saling melebur, kualitas pemilihan turun, biaya token meledak. Menyembunyikan tool dari model sama sekali juga nggak bisa — dia jadi nggak tahu apa yang ada.

## Solusinya: sistem laci tiga lapis

Tools diorganisir kayak perpustakaan beneran — katalognya selalu kelihatan, tapi lo cuma bawa rak yang lo butuhin:

| Lapis | Apa itu | Jumlah |
|---|---|---|
| **Always-on** | Tool planning, search, dan manajemen-diri yang tiap request butuhin | 17 |
| **Kategori** | Laci-lacinya — dibuka eksplisit pas task butuh | 22 (+1 shortcut satu keluarga) |
| **Subdomain** | Laci di dalam laci — subset dari kategori besar | 40 |

Saat task mulai, model cuma lihat menu ringkas: nama kategori, jumlah tool, dan contoh trigger. Membuka kategori (`open_tool_category`) memuat schema penuh laci itu plus instruksi pemakaian detail **untuk sisa sesi** — nggak perlu buka ulang. Shortcut satu keluarga (`code_workspace`) membuka lima drawer kode sekaligus buat sesi engineering berat.

## Disiplin pemilihan

Tiga mekanisme yang bikin pemilihan tetap presisi:

1. **Routing eksplisit, bukan similarity search.** Model *milih* kategori lewat namanya, di-resolve router rule-based. Nggak ada embedding retrieval yang menebak "tool mana yang mungkin relevan" — model menalar intent, router mengeksekusi persis permintaannya.
2. **Pengelompokan berdasarkan pemakaian nyata, bukan nama.** Kategori mencerminkan cara kerja yang sesungguhnya: GitHub + Gist satu drawer (ekosistem sama), sementara git *lokal* dan GitHub *remote* sengaja dipisah (domain beda, nggak pernah dicampur). Keluarga `code_exec` yang raksasa dipecah jadi enam drawer granular persis biar "gua cuma mau jalanin pytest" nggak sekalian menyeret terminal + kernel + LSP + operasi file.
3. **Peluruhan hot/cold.** Kategori yang nggak dipakai 3 task terakhir kehilangan deskripsi penuhnya dari menu statis (nama + contoh tetap ada) — payload always-on tetap kecil, dan deskripsi penuh balik otomatis pas kategori jadi hot lagi.

## Kenapa tools-nya bisa dipercaya

Registry-nya kontrak yang diverifikasi, bukan konvensyen. Pemeriksa parity live membandingkan definisi kategori dengan yang benar-benar ter-register saat import, dan melaporkan ghost (didefinisikan tapi tak ter-register), missing tool, dan duplikat. Run terakhir: **semua nol**. Tiap penambahan lewat protokol registrasi empat titik yang eksplisit — lihat [keputusan registry](../decisions/003-explicit-tool-registry.md).

Lanjut ke: [Memori Berlapis](memory.md) — gimana agent nggak pernah kehilangan benang merah.
