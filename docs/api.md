# Kontrak API Bemai

Versi 1 — dipakai bersama front-end dan back-end. Kalau ada perubahan bentuk JSON,
diubah di dokumen ini dulu, baru di kode.

Base URL: `/api` (saat pengembangan: `http://127.0.0.1:8000/api`)

## Aturan umum

- Semua respons JSON, waktu ISO 8601 UTC: `"2026-09-30T13:00:00Z"`
- Nama kelas selalu lengkap: `"VIII C"` (tingkat + rombel). Daftar kelas: VII–IX × A–F = 18 kelas
- Login memakai cookie sesi `httpOnly`, `SameSite=Lax`, `Secure` saat HTTPS.
  Front-end tidak menyimpan token di `localStorage`
- Semua endpoint butuh login kecuali `POST /auth/login`
- Siswa hanya menerima data kelasnya sendiri; penyaringan dilakukan di server, bukan di browser
- Bentuk galat seragam:

```json
{ "error": { "kode": "tidak_berwenang", "pesan": "Hanya guru yang bisa mengunggah materi" } }
```

Status yang dipakai: `400` data tidak valid, `401` belum login, `403` tidak berwenang,
`404` tidak ada, `409` bentrok (NIS ganda), `500` galat server, `502` model AI gagal.

## Akun dan sesi

### POST /auth/login

```json
{ "identitas": "guru@sekolah.sch.id", "kataSandi": "..." }
```

Identitas guru: email. Identitas siswa: NIS. Respons `200`:

```json
{ "pengguna": { "id": 12, "nama": "Bu Rina", "peran": "guru" } }
```

Siswa menambah `"nis": "2024001", "kelas": "VIII C"`. `peran` bernilai `"guru"` atau `"siswa"`.

### GET /auth/saya

`200 { "pengguna": { ... } }` — dipakai front-end saat halaman dimuat ulang.

### POST /auth/logout

`204` tanpa isi.

## Pengguna (guru)

| Endpoint | Keterangan |
| --- | --- |
| `GET /kelas` | `["VII A", "VII B", ...]` |
| `GET /siswa?tingkat=VIII&rombel=C` | daftar siswa, tanpa filter mengembalikan semua |
| `POST /siswa` | buat satu akun: `{nis, nama, tingkat, rombel}` → `{id, kataSandiAwal}` |
| `POST /siswa/impor` | unggah CSV kolom `nis,nama,tingkat,rombel` → `{berhasil, gagal:[{baris, alasan}]}` |
| `POST /siswa/{id}/reset-sandi` | `{kataSandiAwal}` |

Kata sandi awal dikembalikan sekali, ditampilkan guru untuk dibagikan ke siswa.
Kolom sensitif per siswa hanya nama dan kelas; tidak ada alamat, tanggal lahir, atau nilai rapor.

## Materi

```json
{
  "id": 7,
  "mapel": "IPA",
  "tingkat": "VIII",
  "rombel": ["A", "B", "C"],
  "judul": "Sistem Pernapasan Manusia",
  "teks": ["Hidung menyaring udara...", "Alveolus adalah tempat pertukaran gas..."],
  "rangkuman": ["Hidung → laring → trakea → bronkus → paru-paru", "Pertukaran gas terjadi di alveolus"]
}
```

| Endpoint | Keterangan |
| --- | --- |
| `GET /materi?kelas=VIII%20C` | kelas wajib untuk siswa, opsional untuk guru |
| `GET /materi/{id}` | satu materi |
| `POST /materi` | buat materi baru |
| `PUT /materi/{id}` | ubah materi |
| `DELETE /materi/{id}` | hapus materi |
| `POST /materi/unggah` | multipart `file` (.pdf, .docx, .txt) → materi dengan `teks` hasil ekstraksi |

`rombel` kosong berarti materi berlaku untuk semua rombel pada tingkat itu.

## Soal

```json
{
  "id": 31,
  "materiId": 7,
  "topik": "Organ pernapasan",
  "tanya": "Tempat pertukaran gas pada paru-paru disebut...",
  "opsi": ["Bronkus", "Alveolus", "Trakea", "Diafragma"],
  "jawaban": 1,
  "kelas": ["VIII A", "VIII B"]
}
```

| Endpoint | Keterangan |
| --- | --- |
| `GET /soal?kelas=VIII%20A` | soal untuk kelas itu |
| `POST /soal` | tambah soal manual (guru) |
| `POST /soal/generate` | `{materiId, kelas}` → `{usulan:[...]}` — belum disimpan, guru memilih dulu |
| `POST /soal/terbitkan` | `{usulan:[...]}` → `{jumlah}` menyimpan usulan yang dicentang |
| `DELETE /soal/{id}` | hapus soal |

## Latihan

```json
POST /latihan
{ "materiId": 7, "jawaban": [{ "soalId": 31, "pilihan": 1 }, { "soalId": 32, "pilihan": 0 }] }

200
{
  "nilai": 50, "benar": 1, "total": 2,
  "detail": [{ "soalId": 31, "benar": true, "kunci": 1 }, { "soalId": 32, "benar": false, "kunci": 2 }]
}
```

Penilaian dilakukan di server. Front-end tidak pernah menerima kunci jawaban sebelum siswa selesai.

## Chat

```json
POST /chat
{ "pertanyaan": "Apa itu alveolus?" }

200
{ "jawaban": "Alveolus adalah tempat pertukaran gas oksigen dan karbon dioksida terjadi.",
  "sumber": { "materiId": 7, "judul": "Sistem Pernapasan Manusia" },
  "waktu": "2026-09-30T13:02:11Z" }
```

Server yang menyusun konteks: ambil materi kelas siswa, potong sesuai batas panjang,
lalu kirim ke model AI. Kunci API hanya ada di server.

- Tidak ada materi relevan → `200 { "jawaban": null, "alasan": "tidak_ada_materi" }`
  dan front-end menampilkan pesan apa adanya
- Model gagal atau waktu habis → `502 { "error": { "kode": "ai_gagal", ... } }`
- Riwayat chat disimpan di server dan ikut kena retensi 24 jam

## Analisis (guru)

```json
GET /analisis?tingkat=VIII&rombel=A
{
  "ringkasan": [{ "kelas": "VIII A", "jumlahLatihan": 4, "jumlahMateri": 2, "jumlahSoal": 6, "rataRata": 72 }],
  "distribusi": [{ "rentang": "90-100", "jumlah": 1 }],
  "soalTersulit": [{ "soalId": 32, "topik": "Mekanisme pernapasan", "persenBenar": 25, "dikerjakan": 4 }],
  "perMateri": [{ "materiId": 7, "judul": "Sistem Pernapasan Manusia", "rataRata": 68, "jumlahLatihan": 3 }],
  "retensi": { "hasil": 4, "aktivitas": 9, "chat": 6, "terakhirDibersihkan": "2026-09-30T02:00:00Z", "totalDihapus": 12 }
}
```

`GET /dashboard` → `{ "materi": 3, "soal": 6, "latihan": 4, "rataRata": 72, "aktivitasTerbaru": [...] }`

`DELETE /analisis` → hapus seluruh data analisis sekarang (tombol "Hapus data analisis sekarang").

Semua angka dihitung di server, bukan di front-end.

## Kesehatan

`GET /health` → `{ "status": "ok", "waktu": "2026-09-30T13:00:00Z" }`

## Aturan retensi 24 jam

1. Hasil latihan, aktivitas, dan chat dihapus setelah 24 jam lewat penjadwal di server
   (`pg_cron` bila memakai Postgres)
2. Sebelum menghapus, isi dulu tabel `ringkasan_harian` (`tanggal`, `kelas`,
   `jumlahLatihan`, `rataRata`) supaya rekap harian tetap ada
3. Siswa dan guru bisa melihat keadaan retensi dari blok `retensi` di atas

## Bentuk data contoh

`../mocks/data-contoh.json` berisi 5 materi dan 9 soal dalam bentuk yang sama dengan
respons di atas — dipakai untuk seed database dan untuk mengembangkan front-end
sebelum endpoint siap.

## Yang belum disambung di front-end

Front-end sekarang masih membaca dan menulis `localStorage` lewat `src/js/status.js`
(fungsi `muat`, `simpan`, `simpanKe`). Saat endpoint siap, tiga fungsi itu diganti menjadi
panggilan `fetch`, dan ditambahkan satu berkas `src/js/api.js` sebagai satu-satunya tempat
alamat server dan penanganan galat ditulis.
