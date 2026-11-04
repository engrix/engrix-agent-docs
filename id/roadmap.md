# Roadmap — apa yang nyata, apa yang berikutnya

Tidak ada yang didandani di halaman ini. Tiap item menyatakan apa yang ada hari ini dan apa yang tidak.

| Item | Status | Posisinya sekarang |
|---|---|---|
| Loop agent inti, tool, memory | **Rilis** | Dipakai produksi harian |
| Sub-agent dengan pool tool per divisi | **Rilis** | Tiga belas divisi, kontrol admission, bukti mekanis per run, resume pada child yang selesai. Divisi read-only dipagari di host |
| 4 permukaan UI termasuk copilot desktop | **Rilis** | Keempat permukaan dirender dari satu build; shell desktop adalah pembungkus Electron tipis (always-on-top, hotkey global, tray, pengecualian capture) |
| Screen recording (tombol + tool) | **Rilis** | Tombol in-app; dipakai merekam demo repo ini |
| Portable pack + repo backup | **Rilis** | Launcher `engrix.exe`; backup GitHub |
| Pemisahan transport (`main.py` → router per domain) | **Rilis** | `main.py` hanya perakitan app (509 baris, satu route catch-all); 50 route decorator lainnya tinggal di 13 modul under `transport/routes/` |
| Gate kontrak pada tool dan route | **Rilis** | Paritas registry, kontrak kategori/subdomain dengan self-test, snapshot route, sinkron mirror prompt, gate klaim dokumen |
| Capture engine (evaluation) | **Sebagian** | `evaluation/capture.py` merekam apa yang benar-benar dilihat dan dilakukan agent; analisis di atas capture itu belum dibangun |
| ML untuk mengurangi celah informasi | **Sebagian** | Online learning `ml/` sudah ada; tujuan pengurangan celah di bawah belum selesai |
| Overlay desktop yang lebih dalam ke aplikasi lain | **Sebagian** | Copilot always-on-top sudah rilis; interaksi lebih kaya dengan aplikasi host belum |
| COM Office sebagai tool (Word/Excel/PPT) | **Belum mulai** | Ekspor Excel/CSV/PDF tingkat file sudah jalan hari ini; mengendalikan aplikasi Office hidup adalah hal terpisah |

## Yang baru mendarat

Setiap angka di bawah diukur dari tree hidup oleh `scripts/verify_docs_claims.py`, yang menggagalkan dokumen saat ia melenceng.

| Perubahan | Artinya sebenarnya |
|---|---|
| Engine berhenti jadi satu file entry raksasa | `main.py` sekarang 509 baris berisi perakitan app dan satu route catch-all; permukaan HTTP-nya 50 route decorator tersebar di 13 modul domain di `transport/routes/` |
| Sub-agent jadi subsistem nyata | `subagent/` memegang kontrak, evidence, bentuk report, artefak, resume, watchdog, dan worktree — baris "konsep, belum mulai" dari roadmap sebelumnya hilang karena pekerjaannya sudah mendarat |
| Baseline test backend hijau | `349 passed, 13 skipped, 9 xfailed` tanpa kegagalan. Dua kegagalan subprocess yang dulu dimaklumi sebagai celah environment sudah diperbaiki, bukan didokumentasikan |
| Gate klaim jadi gate sungguhan | Gate yang melaporkan PASS sambil mengukur nol lebih buruk daripada tidak ada gate: section pytest dulu mencetak `0 passed` karena `-q` ganda menekan baris ringkasan pytest, dan section event-sync dulu memindai nol file karena pola path-nya tidak pernah cocok. Keduanya sekarang gagal keras pada pemindaian kosong |

**Belum dibangun:** analisis di atas capture engine, interaksi overlay desktop yang lebih kaya, dan kontrol COM Office. Masing-masing dinyatakan di sini sampai benar-benar rilis.

## Pertanyaan terbuka yang jujur

**Sub-agent — apakah output-nya bisa dipercaya?** Ini dulu pertanyaan terbuka; sekarang sudah punya jawaban yang bekerja, dan jawabannya mekanis bukan prosedural. Setiap run child membawa penghitung bukti, verdict yang diturunkan darinya, redaksi rahasia, dan filter injeksi, dan child yang melapor sukses tanpa verifikasi diberi label belum terverifikasi alih-alih dipercaya. Yang *masih* terbuka adalah pertanyaan arbitrase di bawah permukaannya: dua child menyunting file yang sama. Worktree mengisolasi mereka, tapi kebijakan merge untuk edit yang bertabrakan adalah keputusan manusia, bukan sesuatu yang pantas ditebak engine.

**ML — bagaimana kalau rekomendasi berbasis frekuensi menciptakan loop umpan balik?** Tujuannya bukan agent yang "lebih pintar" tapi agent yang lebih *terinformasi*: tool mana yang benar-benar penting minggu ini, kesalahan mana yang berulang lintas sesi. *Bagaimana ia bisa gagal:* kalau model terus diberi makan "apa yang sudah lo pakai", ia tidak pernah menemukan jalur yang lebih baik — jadi sinyal ranking apa pun harus memuat kualitas hasil (apakah task-nya sukses), bukan cuma jumlah pemakaian.

**Overlay desktop — sejauh mana "berjalan di atas aplikasi lain" bisa pergi?** Copilot sudah melayang di atas aplikasi. *Bagaimana kalau ia bisa membaca dokumen yang sedang lo sunting dan bertindak di dalamnya?* Di situlah COM (item berikutnya) dan tool kontrol desktop bertemu — dirancang bersama, bukan ditempel belakangan.

**COM Office — kenapa tool dan bukan layer integrasi lain?** Word, Excel, dan PowerPoint sebagai tool kelas satu akan membuat agent bekerja *di dalam* dokumen hidup (menyunting spreadsheet yang sedang owner buka) alih-alih hanya menghasilkan file. Belum mulai; ekspor tingkat file menutup sebagian kebutuhannya hari ini.

**Bug yang diketahui — kenapa dinyatakan?** Beberapa bug kecil masih ada di berbagai permukaan. Dilacak dan diperbaiki terus-menerus — portofolio yang mengklaim nol bug itu mengklaim nol pemakaian.
