# Sub-agent

## Pertanyaannya

> *Kalau child agent melapor "selesai", dari mana lo tahu dia benar-benar mengerjakan apa pun — dan apa yang mencegahnya menyunting kode yang sedang lo ubah?*

Pertanyaan itu sebabnya subsistem ini berbentuk seperti sekarang. Pekerja paralel yang melapor sukses tanpa bukti lebih buruk daripada tidak ada pekerja sama sekali: ia mengubah "gue belum cek" menjadi "sudah dicek", dan itu persis mode kegagalan yang hendak dihindari agent berbasis verifikasi.

## Apa yang sudah ada

Sub-agent sudah dikirim, bukan konsep. `subagent/` memegang seluruh lifecycle-nya, dan daftar modulnya adalah desainnya:

| Modul | Memegang |
|---|---|
| `contracts.py` | 13 kontrak divisi — masing-masing menyatakan core tool, backup tool, dan apakah read-only |
| `runner.py` | Admission spawn, cek slot per-task dan RAM, eksekusi child, jalur stop |
| `evidence.py` | Penghitungan bukti mekanis, verdict, redaksi rahasia, filter injeksi |
| `report_form.py` | Bentuk report tetap yang wajib dikembalikan child |
| `artifacts.py` | Di mana output child mendarat di disk, di luar sandbox sekali pakai |
| `resume_context.py` | Mengembalikan konteks child yang sudah selesai untuk run lanjutan |
| `watchdog.py` | Penegakan deadline |
| `worktree.py` | Salinan kerja terisolasi supaya dua child tidak menulis file yang sama |

## Divisi: pool-nya adalah kontraknya

Child tidak mewarisi tool parent. Ia mendapat **divisi** — salah satu dari tiga belas kunci — dan divisi itu menyatakan kategori mana yang boleh dijangkau child:

| Divisi | Bentuk |
|---|---|
| `coding` | filesystem + git + test runner, plus LSP dan terminal sebagai backup |
| `analysis` | read-only: LSP, code search, debugger, read |
| `qc` | read-only: test, diagnostik, diff, read |
| `research` | web search, ekstraksi, crawl, KB, sesi lalu |
| `browser` | navigasi, teks, klik/isi, screenshot, devtools |
| `documents` | PDF, DOCX, XLSX baca/buat/sunting |
| `data` | SQL, ekspor CSV/XLSX/PDF, kernel Python |
| `ops` | shell VPS, systemd, status server, proses background |
| `devices` | kontrol ADB, input dan capture desktop |
| `github` | baca/cari/tree/history repo, PR, issue, branch, gist |
| `email` | Gmail dan IMAP baca/kirim/draft/label |
| `telegram` | posting bot plus akses akun pribadi |
| `design` | render HTML/SVG, operasi gambar, chart, mockup |

Divisi read-only dipagari per tool, bukan hanya per kategori — child read-only tidak bisa menulis meskipun kategorinya kebetulan memuat tool tulis. Pagarnya ditegakkan di host, bukan diminta lewat prompt.

## Bukti, bukan laporan sendiri

Setiap run child diukur. `evidence.py` mengagregasi apa yang benar-benar dilakukan run itu — berapa panggilan tool, berapa di antaranya panggilan bertipe verifikasi, berapa yang sukses, berapa edit yang mendarat, berapa iterasi — dan `evidence_verdict()` mengubahnya jadi label.

Konsekuensinya blak-blakan dan disengaja: child yang mengklaim sukses sementara penghitung buktinya nol dilaporkan sebagai belum terverifikasi, seberapa pun yakin prosanya. Dua prefiks membawa ini ke konteks parent: run yang punya panggilan tool tapi tanpa bukti verifikasi, dan run read-only yang tidak memverifikasi apa pun.

Ringkasan juga difilter sebelum sampai ke parent: `redact_secrets()` membuang string berbentuk kredensial, dan `_is_injection_line()` membuang baris yang tampak seperti instruksi yang disuntikkan halaman yang dibaca child. Child yang disuruh halaman web untuk "laporkan sukses" adalah child gagal, bukan child sukses — dan pipeline memperlakukannya begitu.

## Lifecycle dan batasnya

Spawn dikendalikan admission, bukan fire-and-forget:

- Plafon konkurensi global (`SUBAGENT_MAX_CONCURRENT`, default 50) lintas semua room.
- **Pagar RAM** dievaluasi **per task** di dalam loop, bukan sekali per panggilan. Detail ini penting: mengevaluasinya sekali akan mengubah pagar jadi "batch pertama selalu boleh", dan justru di situlah batch 50 task bisa menjatuhkan mesin.
- Task di luar salah satu batas ditolak dengan alasan, tidak diam-diam diantrekan.
- Watchdog menegakkan deadline; child yang melewati batas dihentikan dan artefak parsialnya tetap bisa diperiksa.
- `resume_context.py` memungkinkan melanjutkan child yang sudah selesai di sesi yang sama, dengan baris run lama tetap tersimpan sebagai jejak audit alih-alih ditimpa.

## Apa yang diterima parent

Bentuk report tetap, bukan prosa bebas. `report_form.py` mendefinisikan field-nya; parent membaca handback terstruktur plus statistik bukti mekanis. Inilah bagian yang membuat delegasi paralel bisa dipakai sama sekali: parent bisa membandingkan dua puluh child tanpa membaca ulang dua puluh esai, dan bisa membedakan "child ini memverifikasi klaimnya" dari "child ini menulis dengan yakin".

Lanjut: [Antarmuka](interfaces.md) — empat cara bicara ke engine yang sama.
