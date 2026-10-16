# ADR-008 — Empat Permukaan dari Satu Build

**Status:** Diterima

> *Pertanyaan yang dijawab ADR ini:* **Gimana empat permukaan UI tetap identik tanpa maintenance dikali empat?**

## Masalah

Agent yang hidup di desktop lo butuh UI yang kontradiktif: workspace penuh buat kerja dalam, dan teman kecil yang selalu tersedia dan melayang di atas aplikasi lain. Membangunnya sebagai aplikasi terpisah (web app + desktop app) berarti logika frontend terduplikasi, perawatan dobel, dan permukaan yang saling meleset.

## Solusi

**Satu build frontend, empat mode.** UI-mode store memilih permukaan saat runtime:

| Mode | Bentuk |
|---|---|
| Full | Workspace: chat, explorer, artifact canvas, review diff |
| Panel | Panel 380px melayang di atas workspace |
| Bubble | Satu tombol brand dengan dot status live |
| Desktop | Jendela Electron frameless, always-on-top, tray + hotkey global |

Shell Electron sengaja tipis: dia memuat **build yang dilayani yang sama** dengan query flag `?ui=desktop` (secara eksplisit menang atas preferensi tersimpan, dan tidak pernah menyimpan dirinya), dan tidak pernah menggandakan engine — health check mendeteksi engine yang sudah jalan dan menyambung ke sana.

## Konsekuensi

- Fitur yang dibangun sekali (chat streaming, approval file, upload) tersedia di semua permukaan di momen yang sama saat dia rilis.
- Jendela desktop bisa berperilaku seperti copilot beneran — *di atas* aplikasi lain, muncul tanpa mencuri fokus, anti screen-capture — sementara isinya nol logika bisnis.
- Satu kendala nyata: shell desktop butuh engine yang dilayani lokal, yang dijamin oleh arsitektur satu proses (ADR-001) sejak awal.
