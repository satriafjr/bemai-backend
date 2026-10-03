import { SEED } from './data-contoh.js';
import { KEY, ROMBEL, TTL_HARI, kodeKelas } from './konstanta.js';

export const status = {
  db: muat(),
  kelasSiswa: 'VIII A',
  filterTingkat: 'semua',
  filterRombel: 'semua',
  role: 'student'
};

export function muat() {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      const d = JSON.parse(raw);
      if (d && Array.isArray(d.materi)) return migrasi(d);
    }
  } catch (e) {}
  const awal = migrasi(JSON.parse(JSON.stringify(SEED)));
  simpanKe(awal);
  return awal;
}
export function simpanKe(d) { try { localStorage.setItem(KEY, JSON.stringify(d)); } catch (e) {} }
export function simpan() { simpanKe(status.db); }

export function migrasi(d) {
  d.hasil = d.hasil || []; d.aktivitas = d.aktivitas || []; d.chat = d.chat || [];
  d.materi.forEach((m) => { if (!Array.isArray(m.rombel)) m.rombel = ROMBEL.slice(); });
  d.soal.forEach((s) => {
    if (!Array.isArray(s.kelas)) {
      const m = d.materi.find((x) => x.id === s.materiId);
      s.kelas = [m ? m.kelas : 'VIII'];
    }

    s.kelas = s.kelas.flatMap((k) => (String(k).includes(' ') ? [k] : ROMBEL.map((r) => kodeKelas(k, r))));
  });
  d.hasil.forEach((h) => {
    if (!h.kelas) {
      const m = d.materi.find((x) => x.id === h.materiId);
      h.kelas = m ? kodeKelas(m.kelas, ROMBEL[0]) : 'VIII A';
    }
  });
  d.dihapus = d.dihapus || 0;
  d.versi = 4;
  return d;
}

export function bersihkanDataLama() {
  const batas = Date.now() - TTL_HARI;
  const sebelum = status.db.hasil.length + status.db.aktivitas.length + status.db.chat.length;
  status.db.hasil = status.db.hasil.filter((h) => h.waktu >= batas);
  status.db.aktivitas = status.db.aktivitas.filter((a) => a.waktu >= batas);
  status.db.chat = status.db.chat.filter((c) => c.waktu >= batas);
  const sesudah = status.db.hasil.length + status.db.aktivitas.length + status.db.chat.length;
  const dibuang = sebelum - sesudah;
  if (dibuang) status.db.dihapus = (status.db.dihapus || 0) + dibuang;
  status.db.bersihTerakhir = Date.now();
  simpan();
  return dibuang;
}

export function catat(tipe, judul, hasil, kelasPaksa) {
  const kelas = kelasPaksa || (status.role === 'student' ? status.kelasSiswa : 'guru');
  status.db.aktivitas.unshift({ waktu: Date.now(), tipe, judul, hasil, kelas });
  status.db.aktivitas = status.db.aktivitas.slice(0, 60);
  simpan();
}

bersihkanDataLama();
