# Roadmap — mana yang nyata, mana yang berikutnya

Nggak ada yang dipoles di halaman ini. Tiap item nyatain apa yang udah ada hari ini dan apa yang belum.

| Item | Status | Posisi sekarang |
|---|---|---|
| Loop agent inti, tools, memori | **Shipped** | Dipakai harian di produksi |
| 4 permukaan UI termasuk copilot desktop | **Shipped** | Satu build, shell Electron termasuk |
| Rekam layar (tombol + tool) | **Shipped** | Tombol di-app; dipakai buat rekam demo repo ini |
| Pack portabel + repo backup | **Shipped** | Launcher `engrix.exe`; backup GitHub |
| Sub-agent bantu main agent | **Concept** | Belum digarap — pertanyaan desain terbuka di bawah |
| ML pengurang kekosongan informasi | **Partial** | `ml/` online learning udah ada; tujuan pengurang kekosongan info di bawah belum selesai |
| Overlay desktop yang lebih dalam di aplikasi lain | **Partial** | Copilot always-on-top udah jalan; interaksi kaya dengan app host belum |
| COM Office sebagai tools (Word/Excel/PPT) | **Not started** | Export file Excel/CSV/PDF udah jalan hari ini; kendali aplikasi Office yang hidup itu terpisah |

## Pertanyaan terbuka yang jujur

**Sub-agent — outputnya bisa dipercaya nggak sih?** *Kalau sub-agent ngedit kode sementara main loop lagi di tengah task — siapa yang jadi wasit tulisan yang bertabrakan?* Jawaban kerjanya: mulai read-only (riset, verifikasi, drafting), akses tulis diperoleh per tingkat kepercayaan, dan semua tulisan sub-agent lewat approval gate yang sama dipakai main agent. Belum ada yang dibangun.

**ML — gimana kalau rekomendasi berbasis frekuensi malah bikin lingkaran setan?** Tujuannya bukan agent yang "lebih pintar" tapi yang lebih *terinformasi*: tool apa yang beneran kepake minggu ini, kesalahan apa yang berulang lintas sesi. *Cara gagalnya:* kalau model terus disuapi "yang lo biasa pake", dia nggak bakal nemuin jalan yang lebih baik — makanya sinyal ranking harus masukin kualitas hasil (task-nya sukses nggak), bukan cuma frekuensi pemakaian.

**Overlay desktop — sejauh mana "jalan di atas aplikasi lain" bisa dibawa?** Copilot udah bisa melayang di atas aplikasi. *Gimana kalau dia bisa baca dokumen yang lagi lo edit dan bertindak di dalamnya?* Di titik itulah COM (item berikutnya) dan tool desktop-control ketemu — didesain bareng, bukan disambung paksa.

**COM Office — kenapa tools, bukan layer integrasi lain?** Word, Excel, dan PowerPoint sebagai first-class tools bikin agent bisa kerja *di dalam* dokumen yang hidup (edit spreadsheet yang lagi kebuka), bukan cuma menghasilkan file. Belum dimulai; export level file udah nutup sebagian kebutuhan.

**Bug yang masih ada — kenapa diomongin?** Beberapa bug kecil masih tersebar di beberapa permukaan. Di-track dan diperbaiki terus-menerus — portofolio yang klaim nol bug itu klaim nol pemakaian.
