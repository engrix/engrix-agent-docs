# ADR-007 — Layering Satu Arah

**Status:** Diterima

> *Pertanyaan yang dijawab ADR ini:* **Bagaimana menghentikan codebase diam-diam menumbuhkan import melingkar?**

## Masalah

Codebase yang sudah tumbuh melenceng ke siklus: kode UI mengimpor storage, storage mengimpor loop agent, semuanya mengimpor segalanya. Setiap fitur baru lalu lebih mahal dari sebelumnya, dan kerusakan "kemarin jalan" jadi rutinitas. Peristiwa pemicunya adalah reorganisasi struktural itu sendiri — pertanyaannya bukan cuma *di mana file ditaruh*, tapi *bagaimana strukturnya bisa ditegakkan*.

## Solusi

Engine adalah paket dengan **satu arah dependensi**:

```
config → paths → storage → memory → knowledge → formatting → curation
       → routing → personality → tools → ml → agent → subagent
       → publication → evaluation → transport → app → bootstrap → main
```

Layer atas boleh mengimpor layer bawah; tidak pernah sebaliknya. Kode domain tidak pernah menulis plumbing SQL; orkestrasi tidak pernah membaca file config langsung. Pemisahan itu adalah kontrak perawatan: satu perbaikan logis mendarat di satu layer.

## Apa yang benar-benar ditegakkan, dan apa yang tidak

Ini bagian yang layak dinyatakan presisi, karena "kami punya aturan layering" itu gampang diucapkan dan sulit dimaksudkan.

**Ditegakkan oleh gate:**

- Modul route tidak boleh mengimpor `engrix.main`. `scripts/route_module_check.py` menggagalkan build saat dilanggar, dan juga memverifikasi bahwa aritmatika path `parents[N]` tiap modul route masih menunjuk akar repo yang sebenarnya — kelas bug yang tidak menghasilkan exception, tidak ada test merah, dan fitur yang diam-diam beroperasi di folder yang salah.
- Nama tingkat-modul yang direferensikan tapi tidak pernah di-bound menggagalkan `scripts/module_binding_check.py`. Gate itu ada karena sebuah statement `import` pernah mendarat di dalam docstring: ia jadi teks lembam, `import engrix.main` tetap sukses, semua gate lolos, dan jalur chat melempar `NameError` di turn berikutnya.
- Wiring tool dan kategori dicek terhadap registry hidup (`check_registry_sync.py`, `check_contracts.py`).

**Tidak ditegakkan oleh gate:**

- Arah import lintas-paket secara penuh. Audit dependensi yang memetakan setiap import lintas-paket adalah pekerjaan sekali jalan saat migrasi dan bukan bagian dari repo yang dikirim. Audit itu menemukan satu-satunya dua back-edge nyata saat itu (modul router mengimpor dari loop agent), yang kemudian dibubarkan dengan memindahkan router ke layer bawah — tapi back-edge baru yang diperkenalkan besok akan tertangkap di review, bukan oleh build yang gagal.

Menyatakan celah itu lebih berguna daripada mengklaim seluruh kontraknya dicek mesin. Gate di atas menutup pelanggaran yang benar-benar pernah terjadi; sisanya kontrak saat review dengan sejarah yang terdokumentasi.

## Konsekuensi

- "Perbaikan ini harus ditaruh di mana?" punya tepat satu jawaban benar per perubahan.
- Dua kelas kegagalan yang sudah pernah menggigit codebase ini sekarang jadi gate alih-alih kebiasaan.
- Migrasinya sendiri dieksekusi sebagai ~35 commit berdisiplin (pindah → verifikasi → commit) dengan gate paritas registry hidup sebelum dan sesudah tiap langkah — nol downtime, sepenuhnya bisa dibalik, setiap langkah di-push ke remote backup sebelum menyentuh produksi.
