# Sistem Tool

Fitur paling menentukan dari Engrix Agent: permukaan tool yang besar dan terdaftar eksplisit di balik sistem laci, jadi prompt per-request tetap kecil seberapa besar pun inventarisnya tumbuh. Aritmatikanya tutup persis: `ter-register = terkategori + always-on + 1 meta-tool` — `open_tool_category`, si pembuka laci itu sendiri, sengaja di luar kategori. Setiap angka di halaman ini diukur dari registry hidup oleh `scripts/verify_docs_claims.py`; dokumen ini menggagalkan gate-nya sendiri kalau melenceng.

## Pertanyaannya

> *Bagaimana agent bisa memakai ratusan tool tanpa bingung — dan memilih yang benar?*

Pendekatan naif gagal di skala ini. Memasukkan setiap schema tool ke setiap request membuat prompt membengkak dan model tenggelam: nama yang mirip saling melebur, kualitas pemilihan turun, biaya token meledak. Menyembunyikan tool dari model sama sekali juga tidak bisa — ia tidak tahu apa yang tersedia.

## Solusinya: sistem laci tiga lapis

Tool disusun seperti perpustakaan fisik — katalognya selalu terlihat, tapi lo cuma membawa rak yang lo butuh:

| Lapis | Apa itu | Jumlah |
|---|---|---|
| **Always-on** | Tool planning, search, dan manajemen-diri yang tiap request butuhin | 19 |
| **Kategori** | Laci-lacinya — dibuka eksplisit pas task butuh | 25 |
| **Subdomain** | Laci di dalam laci — subset dari kategori besar | 46 |

Subdomain-nya tidak disebar tipis: ia ada untuk delapan kategori yang cukup besar untuk membutuhkannya — `github` (12), `vps` (7), `security` (6), `browser` (5), `design` (5), `desktop_control` (5), `device_control` (3), `telethon` (3).

Tampilan per-request tetap datar seberapa dalam pun inventarisnya:

```
tiap request ──▶ [ always-on: 19 tool ]
                 [ menu: 25 nama kategori + jumlah + contoh trigger ]   ◀── kecil, statis
                          │
        model memilih berdasarkan niat, satu panggilan:  open_tool_category("github")
                          │
                          ▼
        sisa sesi ──▶ [ laci github: 83 schema penuh ]  ◀── dimuat sekali
                      [ opsi subdomain: repo_code (16) · pr (3) · … ]
```

Saat task dimulai, model melihat menu ringkas: nama kategori, jumlah tool, dan contoh trigger pendek. Membuka kategori (`open_tool_category`) memuat schema penuh laci itu dan instruksi pemakaian detail **untuk sisa sesi** — tidak perlu dibuka ulang. Shortcut keluarga (`code_workspace`) membuka lima laci terkait kode sekaligus untuk sesi engineering berat.

Lacinya sengaja tidak seimbang, karena kerja nyata juga tidak seimbang: `github` (83) dan `vps` (48) adalah ekosistem, sementara `code_search` (2) dan `debugger` (3) bersifat bedah. Satu keluarga `code_exec` dipecah jadi enam laci granular justru supaya "gue cuma mau jalanin pytest" tidak menyeret terminal + kernel + LSP + operasi file sekaligus.

## Disiplin pemilihan

Tiga mekanisme menjaga pemilihan tetap presisi:

1. **Routing eksplisit, bukan pencarian kemiripan.** Model *memilih* kategori berdasarkan nama lewat router berbasis aturan. Tidak ada retrieval embedding yang menebak "tool mana yang mungkin relevan" — model menalar soal niat, dan router me-resolve persis apa yang diminta.
2. **Pengelompokan berdasarkan pemakaian nyata, bukan nama.** Kategori mencerminkan bagaimana kerja benar-benar terjadi: GitHub + Gist berbagi satu laci (ekosistem sama), sementara git *lokal* dan GitHub *remote* sengaja dipisah (domain berbeda, tidak pernah dicampur).
3. **Peredupan hot/cold.** Kategori yang tidak dipakai selama 3 task terakhir kehilangan deskripsi penuhnya dari menu statis (hanya nama dan contoh yang tersisa) — payload always-on tetap kecil, dan deskripsi penuh masuk lagi hanya saat kategori itu jadi hot.

## Kenapa tool-nya bisa dipercaya

Registry adalah kontrak yang diverifikasi, bukan konvensi. `scripts/check_registry_sync.py` membandingkan definisi kategori dengan apa yang benar-benar ter-register saat import dan **gagal keras** pada ghost (didefinisikan tapi tidak ter-register), tool hilang, drift always-on, dan duplikat. `scripts/check_contracts.py` memperluas gagasan yang sama ke literal kategori, subdomain, dan set always-on, dengan self-test yang membuktikan gate-nya memang bisa gagal.

Ini bukan formalitas. Sejarah yang melahirkannya spesifik: lima insiden terpisah di mana satu kategori tool hilang dari jangkauan agent karena satu import paket terlupa. Tidak ada yang crash — tool-nya cuma diam-diam berhenti ada bagi model. Hilang tanpa suara adalah mode kegagalan terburuk sebuah agent, dan gate ini ada untuk membuatnya berisik.

Setiap penambahan melewati protokol registrasi empat titik yang eksplisit — lihat [keputusan registry](../decisions/003-explicit-tool-registry.md).

Lanjut: [Memory Berlapis](memory.md) — bagaimana agent tidak pernah kehilangan benang.
