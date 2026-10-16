# Antarmuka & Jangkauan

## Pertanyaan kritisnya

> *Gimana empat permukaan UI yang beda-beda tetap identik — tanpa bayar maintenance frontend dikali empat?*

Jawaban salahnya: bikin empat aplikasi. Jawaban benarnya: satu aplikasi yang dirender di empat ukuran, dan cuma wrapper desktop-nya yang beneran kode native.

## Empat permukaan, satu engine

Engine chat yang sama bisa diakses lewat empat mode UI, semua dirender dari satu build frontend:

| Mode | Bentuk |
|---|---|
| **Full** | Workspace lengkap: chat, file explorer, artifact canvas, review diff |
| **Panel** | Panel copilot 380px melayang di atas workspace |
| **Bubble** | Satu tombol brand-mark dengan dot status live |
| **Desktop** | Jendela Electron frameless (400×640), always-on-top *di atas aplikasi lain*, hotkey global, tray icon, anti screen-capture |

```
satu build (frontend/dist)
    │
    ├─ full    workspace    ← browser, route default
    ├─ panel   380px        ← route sama, flag ui-mode
    ├─ bubble  tombol       ← route sama, flag ui-mode
    └─ desktop jendela       ← shell Electron muat dist via ?ui=desktop
                               (frameless · always-on-top · hotkey global · tray)
```

Shell desktop sengaja tipis: dia memuat build yang sama dengan flag `?ui=desktop` dan tidak pernah menggandakan engine — health check mendeteksi engine yang sudah jalan dan menyambung ke sana. Satu codebase, satu dist, empat permukaan.

## Apa saja yang bisa agent jangkau

Inventaris tool (detail di [sistem tool](tool-system.md)) memberi agent jangkauan nyata lintas lingkungan:

- **Mesin lokal** — terminal ter-sandbox, filesystem, Python kernel persisten, tool kode semantik LSP, debugger, test runner
- **Browser** — dual-engine: fork Firefox anti-deteksi untuk otomasi/multi-akun, dan Chrome asli owner via CDP pas task butuh sesi login asli (dengan guard profil terproteksi)
- **Perangkat** — kontrol Android penuh via ADB (tap/swipe/ketik/install/scrcpy) dan kontrol desktop Windows native (lihat/klik/ketik di jendela mana pun, UI Automation, template matching piksel)
- **Remote** — administrasi VPS berbasis SSH: shell (termasuk PTY persisten), filesystem remote penuh, transfer file, systemd, port forwarding
- **Komunikasi** — manajemen kanal Telegram bot + akses akun personal, email via Gmail API dan IMAP
- **Riset keamanan** — pipeline recon→scan→exploit, OSINT, threat intel, reverse engineering biner
- **Git/GitHub** — operasi repo lokal dan administrasi GitHub remote penuh

## Deployment

Pack portabel membundel source, virtual environment, dan build frontend di belakang satu launcher `engrix.exe` — pindahkan foldernya ke path mana pun di mesin, klik dua kali. Engine-nya sendiri tetap proses lokal biasa (dia butuh akses hardware beneran: kamera, ADB, kontrol desktop), sementara service pendukung jalan di Docker Compose.
