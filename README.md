# Bemai — Chatbot Pembelajaran SMP Muhammadiyah

Asisten belajar berbasis materi sekolah. Guru mengisi materi, siswa bertanya dan berlatih,
hasilnya terbaca guru. Prototipe untuk PKM.

## Struktur

```
bemai/
  frontend/
    index.html                halaman (markup saja)
    assets/logo-muhammadiyah.svg
    src/styles/
      dasar.css               variabel warna, tipe teks, tombol, kartu, form
      tata-letak.css          rangka aplikasi: sidebar, topbar, grid, halaman login
      halaman.css             gaya tiap halaman: chat, kuis, nilai, analisis, modal
    src/js/
      konstanta.js            nama aplikasi, daftar tingkat & rombel, kunci penyimpanan
      data-contoh.js          data awal (5 materi IPA/Matematika/B.Indonesia + 9 soal)
      util.js                 pemilih elemen, escaping teks, format tanggal
      status.js               penyimpanan lokal, migrasi data, retensi 24 jam
      seleksi.js              query data: materi per kelas, soal per kelas, hasil per kelas
      ui.js                   navigasi halaman, modal, notifikasi
      siswa/
        chat.js               tanya jawab dengan chatbot
        materi.js             daftar materi kelas + tombol tanya ke chatbot
        latihan.js            pilih materi, kerjakan soal, nilai
        rangkuman.js          rangkuman otomatis dari materi
        riwayat.js            riwayat latihan & pertanyaan siswa
      guru/
        dashboard.js          kartu ringkas + aktivitas terbaru
        materi.js             kelola materi
        soal.js               kelola soal + generate soal dari materi
        upload.js             unggah dokumen (tempel teks)
        analisis.js           analisis hasil belajar, catatan teknis, reset data
      main.js                 pemetaan aksi tombol + titik masuk aplikasi
  backend/                    dikerjakan tim back-end (lihat docs/api.md)
  docs/api.md                 kontrak API antara front-end dan back-end
  mocks/data-contoh.json      contoh isi database (materi & soal)
```

## Menjalankan

Front-end memakai ES module, jadi harus dibuka lewat server lokal (tidak bisa klik dua kali).

```
cd frontend
python3 -m http.server 8899
```

lalu buka http://127.0.0.1:8899 — atau, kalau sudah ada Node:

```
cd frontend
npm run dev
```

Versi satu berkas (`../bemai-prototype.html`) tetap disimpan untuk demo cepat tanpa server.

## Pembagian kerja

Front-end memegang semua yang dilihat dan disentuh pengguna: markup, gaya, alur halaman,
state tampilan, serta seluruh panggilan data. Back-end memegang database, akun, penilaian,
analisis, dan pemanggilan model AI.

Semua komunikasi lewat `docs/api.md`. Bentuk JSON tidak diubah sepihak.

## Konvensi

- Berkas gaya: satu berkas satu lapisan (dasar, tata letak, halaman)
- Berkas JS: satu berkas satu tanggung jawab, impor eksplisit antar berkas
- State global hanya di `status.js`, diakses sebagai `status.db`, `status.kelasSiswa`
- Kelas selalu ditulis lengkap: `"VIII C"` (tingkat + rombel), bukan `"VIII"`
- Data analisis (hasil latihan, aktivitas, chat) otomatis dibuang setelah 24 jam

## Kondisi sekarang

Sudah jalan: login dua peran, chat menjawab dari materi kelas siswa, latihan + penilaian,
rangkuman, riwayat, dashboard guru, kelola materi, kelola soal, unggah dokumen (tempel teks),
analisis per tingkat dan per rombel, serta pembersihan data analisis 24 jam.

Belum tersambung: model bahasa (jawaban chat masih pencarian kata kunci di materi),
database, akun asli, dan ekstraksi PDF/DOCX. Ketiganya bergantung pada back-end.

## Pembahasan, latihan ulang, dan edit

- Setelah mengumpulkan latihan, siswa melihat jawaban sendiri, kunci, dan pembahasan guru.
  Soal lama tanpa pembahasan menampilkan kutipan materi yang memuat jawaban benar jika tersedia;
  jika tidak, aplikasi memberi tahu bahwa penjelasan belum ditambahkan.
- Tombol **Coba lagi** hanya mengulang soal salah atau belum dijawab. Setiap percobaan
  disimpan terpisah, ikut dihitung dalam dashboard, dan tetap mengikuti retensi 24 jam.
  Hasil ulang memiliki `ulangDari` yang menunjuk ID percobaan sebelumnya.
- Guru dapat memilih **Edit** pada daftar materi dan bank soal. Perubahan mempertahankan ID,
  hubungan materi–soal, dan nilai terdahulu. Pembatalan tidak menyimpan perubahan.
- Editor materi mencakup judul, mata pelajaran, tingkat, rombel, isi, dan rangkuman.
  Kelas tujuan soal terkait tidak otomatis berubah; periksa lewat editor soal.
- Editor soal mencakup materi sumber, pertanyaan, pilihan, kunci, kelas tujuan, dan
  `pembahasan` opsional. Pembahasan juga tersedia saat menambahkan soal manual;
  soal definisi otomatis menyimpan penjelasan dari materi sumber.

Pemeriksaan browser: jalankan server lokal terlebih dulu, lalu gunakan Node dan Playwright
(dengan Chromium terpasang) untuk menjalankan `node tests/rendering.cjs` dan
`node tests/learning.cjs`. Pengujian memakai penyimpanan browser terpisah dari data demo pengguna.
