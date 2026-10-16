# ADR-007 — Layering Satu Arah yang Diverifikasi Live

**Status:** Diterima

> *Pertanyaan yang dijawab ADR ini:* **Gimana cara mencegah codebase diam-diam tumbuh circular import?**

## Masalah

Codebase yang tumbuh melorot ke cycle: kode UI meng-import storage, storage meng-import loop agent, semuanya meng-import semuanya. Tiap fitur baru jadi lebih mahal dari yang sebelumnya, dan "kemarin masih jalan" jadi rutinitas. Pemicu di sini adalah reorganisasi struktural itu sendiri — pertanyaannya bukan cuma *file pindah ke mana*, tapi *bagaimana membuat struktur itu bisa ditegakkan*.

## Solusi

Engine adalah satu paket dengan **11 layer satu arah**:

```
config → storage → memory → knowledge → formatting → curation
       → routing → personality → tools → ml → agent → bootstrap → main
```

Layer tinggi boleh meng-import layer rendah; tidak pernah sebaliknya. Kode domain tidak pernah menulis plumbing SQL; orkestrasi tidak pernah membaca file konfigurasi langsung. Pemisahan adalah kontrak perawatan: satu perbaikan logis mendarat di satu layer.

Aturannya diverifikasi, bukan cuma cita-cita: skrip audit dependensi memetakan setiap import lintas paket dan menandai pelanggaran — tool inilah yang menemukan hanya dua back-edge nyata (router meng-import dari loop agent) saat restrukturisasi, yang lalu dilarutkan dengan memindahkan router turun satu layer.

## Konsekuensi

- "Perbaikan ini ditaruh di mana?" punya satu jawaban benar per perubahan.
- Cycle muncul di langkah audit, bukan sebagai error import saat runtime.
- Migrasinya sendiri dieksekusi sebagai ±35 commit disiplin (pindah → verifikasi → commit) dengan gate parity registry live sebelum dan sesudah tiap langkah — zero-downtime, sepenuhnya reversible, tiap langkah di-push ke remote backup sebelum produksi disentuh.
