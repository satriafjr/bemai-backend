# Back-end Bemai

Folder ini untuk tim back-end. Kontrak lengkapnya di `../docs/api.md` — bentuk JSON di sana
yang dipakai front-end, jadi kalau ada perubahan, ubah dokumennya dulu.

## Urutan pengerjaan yang disarankan

1. Rangka proyek + Postgres + migrasi tabel (`pengguna`, `materi`, `soal`, `hasil`,
   `aktivitas`, `chat`, `ringkasan_harian`)
2. Login guru dan siswa, cookie sesi, `GET /auth/saya`, middleware peran
3. Materi: daftar terfilter kelas, tambah, ubah, hapus
4. Soal: daftar per kelas, tambah manual, generate dari materi, terbitkan
5. `POST /chat`: susun konteks dari materi kelas siswa, panggil model AI, simpan riwayat
6. Latihan: penilaian di server, simpan hasil
7. Analisis: ringkasan per tingkat dan per rombel, soal tersulit, KPI dashboard
8. Unggah PDF/DOCX, impor CSV siswa, reset kata sandi
9. Retensi 24 jam lewat penjadwal, isi `ringkasan_harian` sebelum menghapus
10. Swagger, data seed, HTTPS, URL staging

## Yang tidak boleh dilakukan

- Menaruh kunci API model AI di berkas front-end atau mengirimnya ke browser
- Mengembalikan seluruh isi tabel tanpa filter kelas
- Menyerahkan perhitungan nilai atau analisis ke front-end
- Menyimpan data siswa di luar yang dipakai fitur: identitas cukup nama dan kelas

## Yang dibutuhkan front-end lebih dulu

`POST /auth/login`, `GET /auth/saya`, `GET /materi?kelas=`, `GET /soal?kelas=`,
`POST /chat`, `POST /latihan`, `GET /analisis`, `GET /dashboard`.
Delapan endpoint itu sudah cukup untuk mengganti seluruh penyimpanan lokal di front-end.
