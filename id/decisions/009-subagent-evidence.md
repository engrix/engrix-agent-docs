# ADR-009 — Sub-agent Dinilai dari Bukti, Bukan dari Laporannya Sendiri

**Status:** Diterima

> *Pertanyaan yang dijawab ADR ini:* **Kalau child agent bilang "selesai", apa di sistem ini yang membantahnya?**

## Masalah

Pekerja paralel menarik karena tepat satu alasan: throughput. Ia berbahaya karena tepat satu alasan: parent tidak bisa melihat apa yang terjadi. Child mengembalikan ringkasan — output model, dihasilkan setelah kejadian, tidak membawa otoritas apa pun. Ringkasan yakin atas pekerjaan yang tidak pernah terjadi tidak bisa dibedakan dari ringkasan yakin atas pekerjaan yang benar-benar terjadi, kecuali ada sesuatu yang mekanis di antara keduanya.

Desain naif ("spawn child, kumpulkan teksnya, percaya teksnya") mengubah *belum terverifikasi* menjadi *terverifikasi* dalam satu langkah. Untuk agent yang seluruh proposisi nilainya adalah memeriksa klaimnya sendiri, itu bukan fitur throughput — itu korupsi pada intinya.

## Solusi

Tiga keputusan, masing-masing menutup satu lubang.

**1. Pool tool adalah kontrak, bukan warisan.** Child tidak mendapat laci parent. Ia mendapat *divisi* — salah satu dari tiga belas kontrak bernama, masing-masing menyatakan core tool, backup tool, dan status read-only. Divisi read-only dipagari **per tool di host**, bukan diminta lewat prompt, karena pagar tingkat prompt hanyalah saran.

**2. Setiap run diukur.** `subagent/evidence.py` mengagregasi apa yang benar-benar dilakukan run itu — panggilan tool, panggilan bertipe verifikasi, keberhasilan, edit, iterasi — dan menurunkan verdict dari penghitungnya. Child dengan panggilan tool tapi tanpa verifikasi membawa penanda belum-terverifikasi eksplisit ke konteks parent. Child yang tidak menghasilkan panggilan tool sama sekali dilaporkan begitu, bukan dirangkum sebagai "selesai".

**3. Bentuk report-nya tetap.** `subagent/report_form.py` mendefinisikan field-nya. Parent membaca handback terstruktur plus statistik mekanis, jadi dua puluh child bisa dibandingkan tanpa membaca ulang dua puluh esai — dan perbedaan antara "terverifikasi" dan "menulis dengan yakin" terlihat di datanya, bukan disimpulkan dari nadanya.

Dua filter duduk di jalur pulang: `redact_secrets()` membuang string berbentuk kredensial, dan deteksi baris injeksi membuang instruksi yang datang dari halaman yang dibaca child. Child yang disuruh situs web untuk melaporkan sukses adalah child **gagal**. Memperlakukan output-nya sebagai data alih-alih perintah adalah inti persoalannya.

## Konsekuensi

- Delegasi paralel jadi bisa dipakai untuk pekerjaan yang hasilnya akan ditindaklanjuti parent, bukan cuma untuk draft.
- Sebagian child sah-sah saja mengembalikan nol bukti — run riset read-only yang hanya membaca dan menyintesis. Mereka dilabeli belum-terverifikasi-by-design alih-alih lolos diam-diam; labelnya jujur, bukan menghukum.
- Kontrol admission adalah bagian dari keputusan yang sama: plafon konkurensi global dan pagar RAM yang dievaluasi **per task di dalam loop**, bukan sekali per panggilan. Mengevaluasinya sekali akan mengubah pagar jadi "batch pertama selalu boleh" — dan justru di situlah batch lima puluh task menjatuhkan mesin.
- Biayanya adalah upacara: kontrak yang harus dinyatakan, bukti yang harus dihitung, bentuk report yang harus diisi. Biaya itu dibayar sekali per subsistem dan menyelamatkan parent dari memverifikasi ulang klaim tiap child dengan tangan.
