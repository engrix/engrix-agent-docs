# ADR-004 — Provider Sebagai Konfigurasi, Bukan Kode

**Status:** Diterima

> *Pertanyaan yang dijawab ADR ini:* **Gimana kalau owner mau nambah provider jam 2 pagi tanpa nyentuh kode?**

## Masalah

Model provider terus berubah: endpoint baru, nama model baru, skema auth baru, opsi reasoning-effort baru. Provider yang di-hardcode berarti tiap perubahan provider = perubahan kode — review, redeploy, dan risiko ke seluruh engine cuma buat ganti satu endpoint.

## Solusi

Setiap provider adalah **file YAML**: base URL, alur auth, daftar model, dan kapabilitas per-model (termasuk opsi reasoning-effort bersarang) seluruhnya hidup di konfigurasi. Engine memuat registry saat startup dan mengekspos hasilnya ke UI lewat satu API — frontend tidak pernah membaca file konfigurasi langsung, jadi sumber kebenarannya persis satu.

## Konsekuensi

- Menambah atau memensiunkan provider = edit file YAML, nol perubahan kode.
- Model picker di UI dan jalur request di engine tidak mungkin saling contradict — dua-duanya baca registry yang sama.
- Opsi per-model (kayak level reasoning effort) adalah data, bukan kode UI — picker me-render apa pun yang dideklarasikan YAML.
