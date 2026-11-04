# ADR-006 — Pemadatan yang Mempertahankan Inti (Desain Memory)

**Status:** Diterima

> *Pertanyaan yang dijawab ADR ini:* **Bagaimana kalau pemadatan justru menghapus persis detail yang dibutuhkan task nanti?**

## Masalah

Kebutuhan aslinya blak-blakan:

> *"Asisten yang bisa melakukan apa saja, jalan di mana saja, dan tidak pernah kehilangan konteks."*

Chat history sendirian gagal persis di sini. Ia membengkak sampai model kehilangan bagian awal di tengah, atau terpotong dan agent lupa task-nya sendiri. Dan lupa bukan satu masalah — setidaknya ada lima: lupa fakta, lupa langkah sekarang, lupa apa yang sudah diverifikasi, lupa sesi lalu, lupa apa yang dibahas percakapan saudara.

## Solusi

Perlakukan "tidak pernah lupa" sebagai sekumpulan **store berlapis**, masing-masing memiliki satu jenis lupa — semuanya dirancang di sekitar prinsip yang sama: *padatkan agresif, tapi selalu pertahankan intinya.*

| Jenis lupa | Store |
|---|---|
| Fakta yang dinyatakan dalam sesi | Ekstraksi fakta mekanis (nol halusinasi, difilter stopword) |
| Di mana saya di task ini | Blok posisi task yang disuntik di **setiap** turn model |
| Apa yang sudah dicek | State verifikasi, dengan kesegaran — kesimpulan tidak bisa hidup lebih lama dari buktinya |
| Apa yang terjadi di sesi lalu | Indeks episode yang diformat saat dibutuhkan |
| Apa yang dibahas percakapan lain | Indeks topik berisi pointer; konten diambil dari vector store saat perlu |

Detail yang menanggung beban: output tool panjang di history **dipadatkan saat dibaca, bukan dihapus**. Layer yang sama yang menambahkan pesan memiliki cap yang diterapkan saat history dibaca untuk model — jadi tampilan model tetap koheren sementara database menyimpan rekaman penuh yang masih bisa ditampilkan UI. Di dalam satu room task, makin dalam chat berarti *makin banyak pemadatan, inti tetap sama*: konteks room mengecil seiring waktu, bukan membesar.

Store verifikasi adalah bagian yang paling sering dilewatkan desain memory lain. Agent yang mengingat kesimpulan tapi tidak mengingat buktinya akan dengan yakin mengulang kesimpulan basi — jadi rekaman *apa yang sudah dicek* diperlakukan sebagai memory juga, dengan sinyal kebasian alih-alih centang permanen.

## Konsekuensi

- Agent di jam keempat masih membawa kerangka task-nya di depan mata setiap turn.
- "Memory" hasil halusinasi ditekan secara struktural: fakta hanya masuk lewat ekstraksi mekanis, tidak pernah lewat model yang merangkum dirinya sendiri dengan bebas.
- Pengalaman lintas sesi menumpuk: task baru mulai lebih pintar karena ringkasan task lalu hanya berjarak satu retrieval.
- Biaya pemadatan saat-baca adalah adanya dua tampilan atas sesi yang sama (rekaman penuh, tampilan model terpadatkan). Itu disengaja — keduanya jujur, pada tingkat kesetiaan berbeda — tapi artinya setiap debugging "apa yang benar-benar dilihat model" harus membaca tampilan terpadatkan, bukan database.
