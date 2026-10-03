import { SEED } from '../data-contoh.js';
import { ROMBEL, TINGKAT, kodeKelas, tingkatDari } from '../konstanta.js';
import { hasilFilter, materiKelas, materiTingkat, rombelLabel, soalKelas, soalTingkat } from '../seleksi.js';
import { bersihkanDataLama, simpan } from '../status.js';
import { aturRoleUI, bukaModal, toast, tutupModal } from '../ui.js';
import { $, esc, jam } from '../util.js';
import { status } from '../status.js';

export function renderAnalisis() {
  const dibuang = bersihkanDataLama();
  if (dibuang) toast(dibuang + ' baris data lebih dari 24 jam dihapus otomatis');

  $('#filterKelasAnalisis').innerHTML = ['semua', ...TINGKAT].map((k) =>
    `<button class="chipkelas" data-act="status.filterTingkat" data-tingkat="${k}" aria-pressed="${status.filterTingkat === k}">${k === 'semua' ? 'Semua tingkat' : 'Kelas ' + k}</button>`).join('');
  $('#filterRombelAnalisis').innerHTML = status.filterTingkat === 'semua' ? '' : ['semua', ...ROMBEL].map((r) =>
    `<button class="chipkelas" data-act="status.filterRombel" data-rombel="${r}" aria-pressed="${status.filterRombel === r}">${r === 'semua' ? 'Semua rombel' : status.filterTingkat + ' ' + r}</button>`).join('');
  $('#filterRombelAnalisis').style.display = status.filterTingkat === 'semua' ? 'none' : 'flex';

  $('#ttlInfo').innerHTML =
    `<b>Data analisis disimpan 24 jam saja.</b> Hasil latihan &amp; riwayat yang lebih tua dihapus otomatis supaya tidak menumpuk di database — jadi semua angka di halaman ini hanya untuk <b>1 hari terakhir</b>.` +
    `<div class="small" style="margin-top:8px">Tersimpan sekarang: <b>${status.db.hasil.length}</b> hasil latihan · <b>${status.db.aktivitas.length}</b> aktivitas · <b>${status.db.chat.length}</b> riwayat chat. Terakhir dibersihkan ${jam(status.db.bersihTerakhir || Date.now())} · total sudah dihapus otomatis: <b>${status.db.dihapus || 0}</b> baris.</div>` +
    `<div class="btnrow" style="margin-top:10px"><button class="btn danger small" data-act="hapusAnalisis"> Hapus data analisis sekarang</button></div>`;

  const barisRingkasan = (judul, cocok, materiN, soalN) => {
    const h = status.db.hasil.filter(cocok);
    const r = h.length ? Math.round(h.reduce((a, b) => a + b.nilai, 0) / h.length) : 0;
    return `<div style="margin-bottom:14px">
      <div class="stat"><span>${judul} <span class="small muted"> ${h.length} latihan · ${materiN} materi · ${soalN} soal</span></span><b>${h.length ? r + '%' : '—'}</b></div>
      <div class="bar"><span style="width:${r}%"></span></div></div>`;
  };
  if (status.filterTingkat === 'semua') {
    $('#judulRingkasan').textContent = 'Ringkasan per Tingkat';
    $('#ringkasanKelas').innerHTML = TINGKAT.map((t) =>
      barisRingkasan('Kelas ' + t, (x) => tingkatDari(x.kelas) === t, materiTingkat(t).length, soalTingkat(t).length)).join('') +
      '<p class="small muted">Pilih salah satu tingkat di atas untuk melihat rincian per rombel (AF).</p>';
  } else {
    $('#judulRingkasan').textContent = 'Ringkasan Kelas ' + status.filterTingkat + ' per Rombel';
    $('#ringkasanKelas').innerHTML = ROMBEL.map((r) => {
      const kode = kodeKelas(status.filterTingkat, r);
      return barisRingkasan(kode, (x) => x.kelas === kode, materiKelas(kode).length, soalKelas(kode).length);
    }).join('') +
      '<p class="small muted">Kelas tanpa latihan ditandai "—". Angka dihitung dari latihan yang benar-benar dikerjakan siswa kelas tersebut.</p>';
  }

  const hasil = hasilFilter();
  const labelKelas = status.filterTingkat === 'semua' ? 'semua kelas'
    : (status.filterRombel === 'semua' ? 'kelas ' + status.filterTingkat : 'kelas ' + status.filterTingkat + ' ' + status.filterRombel);
  const nilai = hasil.map((h) => h.nilai);
  const bucket = [['90100', (n) => n >= 90], ['8089', (n) => n >= 80 && n < 90], ['7079', (n) => n >= 70 && n < 80], ['<70', (n) => n < 70]];
  $('#distribusiNilai').innerHTML = nilai.length
    ? bucket.map(([label, fn]) =>
        `<div class="list-item"><span>${label}</span><b>${nilai.filter(fn).length} latihan</b></div>`).join('')
      + `<p class="small muted" style="margin-top:10px">Rata-rata ${Math.round(nilai.reduce((a, b) => a + b, 0) / nilai.length)} dari ${nilai.length} latihan (${labelKelas}).</p>`
    : '<p class="muted">Belum ada latihan yang dikerjakan ' + labelKelas + '.</p>';

  const agg = {};
  hasil.forEach((h) => h.detail.forEach((d) => {
    agg[d.soalId] = agg[d.soalId] || { benar: 0, total: 0 };
    agg[d.soalId].total++;
    if (d.benar) agg[d.soalId].benar++;
  }));
  const urut = Object.entries(agg).map(([id, v]) => {
    const s = status.db.soal.find((x) => x.id === id);
    return { soal: s, persen: Math.round((v.benar / v.total) * 100), total: v.total };
  }).filter((x) => x.soal).sort((a, b) => a.persen - b.persen);

  $('#soalSulit').innerHTML = urut.length
    ? urut.slice(0, 5).map((x) => `
        <div class="feature" style="margin-bottom:12px">
          <div class="icon dot ${x.persen < 50 ? 'warn' : x.persen < 80 ? 'mid' : ''}"></div>
          <div><h3>${esc(x.soal.topik || 'Soal')} — ${x.persen}% benar</h3>
            <p class="small muted">${esc(x.soal.tanya)}</p>
            <p class="small muted">Dikerjakan ${x.total} kali</p></div>
        </div>`).join('')
    : '<p class="muted">Belum ada data jawaban.</p>';

  const daftarMateriGuru = status.filterTingkat === 'semua'
    ? status.db.materi
    : status.db.materi.filter((m) => m.kelas === status.filterTingkat && (status.filterRombel === 'semua' || (m.rombel || ROMBEL).includes(status.filterRombel)));
  $('#rincianMateri').innerHTML = daftarMateriGuru.map((m) => {
    const h = status.db.hasil.filter((x) => x.materiId === m.id);
    if (!h.length) return `<div class="list-item"><span>${esc(m.judul)} <span class="tag">kelas ${esc(m.kelas)} — ${esc(rombelLabel(m))}</span></span><span class="tag">belum dikerjakan</span></div>`;
    const r = Math.round(h.reduce((a, b) => a + b.nilai, 0) / h.length);
    return `<div class="list-item"><span>${esc(m.judul)} <span class="tag">kelas ${esc(m.kelas)} — ${esc(rombelLabel(m))}</span><div class="small muted">${h.length} latihan · rata-rata ${r}</div></span>
      <span class="tag ${r >= 80 ? 'green' : 'amber'}">${r >= 80 ? 'baik' : 'perlu penguatan'}</span></div>`;
  }).join('') || '<p class="muted">Belum ada materi untuk kelas ini.</p>';
}

export function hapusAnalisisSekarang() {
  if (!confirm('Hapus semua data analisis (hasil latihan, aktivitas, riwayat chat) sekarang?')) return;
  const jumlah = status.db.hasil.length + status.db.aktivitas.length + status.db.chat.length;
  status.db.hasil = []; status.db.aktivitas = []; status.db.chat = [];
  status.db.dihapus = (status.db.dihapus || 0) + jumlah;
  simpan();
  renderAnalisis();
  toast(jumlah + ' baris data analisis dihapus');
}

export function catatanTeknis() {
  bukaModal('Catatan teknis', 'Apa yang nyata dan apa yang belum',
    `<p><b>Sudah berfungsi di prototype ini</b></p>
    <ul>
      <li>Alur utuh: guru → materi → soal → siswa mengerjakan → hasil terbaca guru.</li>
      <li>Setiap materi &amp; soal punya <b>kelas tujuan</b> lengkap: tingkat (VII/VIII/IX) <b>dan rombel (A–F)</b>. Siswa hanya melihat materi/soal kelasnya; guru bisa menerbitkan ke beberapa kelas sekaligus, mis. VIII A + VIII B.</li>
      <li>Analisis guru <b>dipisah per kelas</b>: filter per tingkat, lalu per rombel, plus ringkasan tiap kelas A–F.</li>
      <li>Chatbot menjawab dengan mencari kalimat relevan di materi sekolah dan menyebutkan sumbernya.</li>
      <li>Latihan dinilai otomatis, hasil &amp; riwayat disimpan di browser.</li>
      <li>Generate soal dari kalimat definisi materi, guru tetap memutuskan terbit atau tidak.</li>
    </ul>
    <p><b>Retensi data: 24 jam</b></p>
    <ul>
      <li>Hasil latihan, aktivitas, dan riwayat chat hanya disimpan <b>1 hari</b>; yang lebih tua dihapus otomatis setiap kali app dibuka — supaya database tidak menumpuk.</li>
      <li>Konsekuensinya: angka analisis adalah kondisi 1 hari terakhir, tidak untuk melihat tren mingguan. Kalau tren mau disimpan, tambahkan tabel <i>ringkasan harian</i> (tanggal, kelas, jumlah siswa, rata-rata) yang ukurannya kecil.</li>
      <li>Di versi database nyata: jalankan penghapusan terjadwal, mis. <code>delete from hasil where waktu &lt; now() - interval '1 day'</code> via pg_cron / Supabase scheduled function.</li>
    </ul>
    <p><b>Belum tersambung (jujur untuk laporan PKM)</b></p>
    <ul>
      <li>Tidak ada LLM. Jawaban chatbot = pencarian kata kunci, bukan model bahasa. Ganti dengan Gemini API memakai pola <i>context stuffing</i>: kirim teks materi + pertanyaan siswa, tanpa vector database/RAG.</li>
      <li>Tidak ada server/database. Data disimpan di localStorage browser, jadi tidak sinkron antar perangkat dan antar siswa.</li>
      <li>Upload PDF/DOCX belum bisa diekstrak di sisi browser.</li>
      <li>Belum ada autentikasi asli; login hanya simulasi peran (kelas siswa masih dipilih manual).</li>
    </ul>
     <div class="btnrow">
       <button class="btn danger" data-act="resetData">Reset data demo</button>
       <button class="btn primary" data-act="tutupModal">Tutup</button>
     </div>`);
}

export function resetData() {
  if (!confirm('Kembalikan semua data demo ke kondisi awal?')) return;
  status.db = JSON.parse(JSON.stringify(SEED));
  simpan();
  tutupModal();
  aturRoleUI();
  toast('Data demo dikembalikan ke awal');
}
