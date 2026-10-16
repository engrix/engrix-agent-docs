# Roadmap — mana yang nyata, mana yang berikutnya

Tidak ada yang dipoles di halaman ini. Tiap item menyatakan apa yang sudah ada saat ini dan apa yang belum.

| Item | Status | Posisi sekarang |
|---|---|---|
| Loop agent inti, tools, memori | **Shipped** | Dipakai harian di produksi |
| 4 permukaan UI termasuk copilot desktop | **Partial (masih di-debug)** | Keempat permukaan sudah jalan; copilot desktop masih di-debug harian. Berikutnya: dua mode yang jelas — mode **asisten** cepat (tanpa lapisan perencanaan, langsung jawab) dan mode **workspace** penuh |
| Rekam layar (tombol + tool) | **Shipped** | Tombol di-app; dipakai buat rekam demo repo ini |
| Pack portabel + repo backup | **Shipped** | Launcher `engrix.exe`; backup GitHub |
| Sub-agent bantu main agent | **Concept** | Belum digarap — pertanyaan desain terbuka di bawah |
| ML pengurang kekosongan informasi | **Partial** | `ml/` online learning sudah ada; tujuan pengurang kekosongan info di bawah belum selesai |
| Overlay desktop yang lebih dalam di aplikasi lain | **Partial** | Copilot always-on-top sudah jalan; interaksi kaya dengan app host belum |
| COM Office sebagai tools (Word/Excel/PPT) | **Not started** | Export file Excel/CSV/PDF sudah berjalan saat ini; kendali aplikasi Office yang hidup itu terpisah |

## Pertanyaan terbuka yang jujur

**Sub-agent — apakah outputnya bisa dipercaya?** *Kalau sub-agent mengedit kode sementara main loop masih di tengah task — siapa yang menjadi wasit tulisan yang bertabrakan?* Jawaban kerjanya: mulai dari read-only (riset, verifikasi, drafting), akses tulis diperoleh per tingkat kepercayaan, dan semua tulisan sub-agent melewati approval gate yang sama dengan yang dipakai main agent. Belum ada yang dibangun.

**ML — bagaimana jika rekomendasi berbasis frekuensi justru menciptakan lingkaran setan?** Tujuannya bukan agent yang "lebih pintar" tetapi yang lebih *terinformasi*: tool apa yang benar-benar terpakai minggu ini, kesalahan apa yang berulang lintas sesi. *Cara gagalnya:* jika model terus disuapi "yang biasa dipakai", ia tidak akan menemukan jalan yang lebih baik — karena itu sinyal ranking harus memasukkan kualitas hasil (berhasil atau tidaknya task), bukan hanya frekuensi pemakaian.

**Overlay desktop — sejauh mana "jalan di atas aplikasi lain" bisa dibawa?** Copilot sudah bisa melayang di atas aplikasi. *Bagaimana kalau ia bisa membaca dokumen yang sedang diedit dan bertindak di dalamnya?* Di titik itulah COM (item berikutnya) dan tool desktop-control bertemu — didesain bersama, bukan disambung paksa.

**COM Office — kenapa tools, bukan layer integrasi lain?** Word, Excel, dan PowerPoint sebagai first-class tools membuat agent dapat bekerja *di dalam* dokumen yang hidup (mengedit spreadsheet yang sedang terbuka), bukan hanya menghasilkan file. Belum dimulai; export level file sudah menutup sebagian kebutuhan.

**Bug yang masih ada — kenapa diakui?** Beberapa bug kecil masih tersebar di beberapa permukaan. Di-track dan diperbaiki terus-menerus — portofolio yang klaim nol bug itu klaim nol pemakaian.
