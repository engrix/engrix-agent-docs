# ADR-001 — Satu Proses Melayani Semua

**Status:** Diterima

> *Pertanyaan yang dijawab ADR ini:* **Kalau frontend dan backend berbeda versi — siapa yang memegang kebenaran?**

## Masalah

Web UI dan API-nya mudah berjauhan kalau di-deploy terpisah: dua pipeline build, konfigurasi CORS, version skew antara yang frontend harapkan dan yang backend layankan, dan deployment multi-langkah buat produk single-owner yang tinggal harus jalan.

## Solusi

Backend FastAPI **melayani build frontend-nya sendiri**. Satu proses, satu port, satu versi — satu deployment adalah satu hal yang dinyalakan. Aplikasi React dibuild jadi aset statis yang engine layankan dari disk; refresh browser langsung dapat build baru tanpa menyentuh proses engine.

## Konsekuensi

- Version skew mustahil secara struktural: UI yang dibuka adalah UI yang engine ini layankan.
- Menambah permukaan UI tidak menambah beban operasional — shell desktop Electron memuat build yang dilayani yang sama lewat query flag.
- Satu proses menuntut disiplin startup yang wajar (health endpoint, graceful shutdown) — yang sebenarnya dibutuhkan juga oleh shell desktop dan tooling restart.
