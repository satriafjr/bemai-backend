import { editMateri, editSoal } from './guru/editor.js';
import { catatanTeknis, hapusAnalisisSekarang, renderAnalisis, resetData } from './guru/analisis.js';
import { hapusMateri, tambahMateri } from './guru/materi.js';
import { generateSoal, sinkronKelasManual, tambahSoalManual, terbitkanSoal } from './guru/soal.js';
import { pilihFile, tempelMateri } from './guru/upload.js';
import { kodeKelas, tingkatDari } from './konstanta.js';
import { geserSorot, pasangSemuaTilt, pasangTilt } from './efek/inti.js';
import { tampilkanView } from './efek/halaman.js';
import { kirimChat } from './siswa/chat.js';
import { batalLatihan, mulaiLatihan } from './siswa/latihan.js';
import { bacaMateri, tanyaMateri } from './siswa/materi.js';
import { buatRangkuman, simpanRangkuman } from './siswa/rangkuman.js';
import { aturRoleUI, bukaSidebar, tampilkanHalaman, tutupModal, tutupSidebar } from './ui.js';
import { $, $$ } from './util.js';
import { status } from './status.js';

export const AKSI = {
  editMateri(el) { editMateri(el.dataset.id); },
  editSoal(el) { editSoal(el.dataset.id); },
  pilihRole(el) {
    $$('.rolebtn').forEach((b) => b.classList.remove('selected'));
    el.classList.add('selected');
    status.role = el.dataset.role;
    $('#loginUser').value = status.role === 'student' ? 'siswa8a' : 'guru.ipa';
    $('#barisKelasSiswa').style.display = status.role === 'student' ? 'block' : 'none';
  },
  masuk() {
    if (status.role === 'student') status.kelasSiswa = kodeKelas($('#loginTingkat').value, $('#loginRombel').value);
    tampilkanView($('#loginView'), () => {
      $('#loginView').style.display = 'none';
      $('#appView').style.display = 'flex';
      $('#appView').classList.add('masuk-view');
      setTimeout(() => $('#appView').classList.remove('masuk-view'), 620);
      aturRoleUI();
    });
  },
  keluar() {
    tampilkanView($('#appView'), () => {
      $('#appView').style.display = 'none';
      $('#loginView').style.display = 'grid';
      $('#loginView').classList.add('masuk-view');
      setTimeout(() => $('#loginView').classList.remove('masuk-view'), 620);
      tutupSidebar();
    });
  },
  bukaSidebar() { bukaSidebar(); },
  tutupSidebar() { tutupSidebar(); },
  bukaHalaman(el) { tampilkanHalaman(el.dataset.page); },
  catatanTeknis() { catatanTeknis(); },
  tutupModal() { tutupModal(); },
  kirimChat() { kirimChat(); },
  chip(el) { kirimChat(el.dataset.q); },
  bacaMateri(el) { bacaMateri(el.dataset.id); },
  tanyaMateri(el) { tanyaMateri(el.dataset.id); },
  keLatihan(el) {
    tutupModal();
    tampilkanHalaman('s-latihan');
    mulaiLatihan(el.dataset.id);
  },
  mulaiLatihan() { mulaiLatihan(); },
  batalLatihan() { batalLatihan(); },
  buatRangkuman() { buatRangkuman(); },
  rangkumanCepat(el) {
    $('#pilihMateriRangkuman').value = el.dataset.id;
    buatRangkuman();
  },
  simpanRangkuman(el) { simpanRangkuman(el.dataset.id); },
  tambahMateri() { tambahMateri(); },
  hapusMateri(el) { hapusMateri(el.dataset.id); },
  bersihkanMateri() { $('#mJudul').value = ''; $('#mTeks').value = ''; },
  generateSoal() { generateSoal(); },
  terbitkanSoal() { terbitkanSoal(); },
  tambahSoalManual() { tambahSoalManual(); },
  pilihFile(el) { pilihFile(el); },
  tempelMateri() { tempelMateri(); },
  resetData() { resetData(); },
  filterTingkat(el) { status.filterTingkat = el.dataset.tingkat; status.filterRombel = 'semua'; renderAnalisis(); },
  filterRombel(el) { status.filterRombel = el.dataset.rombel; renderAnalisis(); },
  pilihSemuaKelas(el) {
    const target = el.dataset.target;
    const t = el.dataset.tingkat;
    $$(`${target} input`).forEach((c) => { if (tingkatDari(c.value) === t) c.checked = true; });
  },
  hapusAnalisis() { hapusAnalisisSekarang(); }
};

document.addEventListener('click', (e) => {
  const el = e.target.closest('[data-act]');
  if (!el) return;
  const fn = AKSI[el.dataset.act];
  if (!fn) return;
  if (el.tagName === 'INPUT' && el.type === 'file') return;
  e.preventDefault();
  fn(el);
});

$('#fileMateri').addEventListener('change', (e) => pilihFile(e.target));
$('#qMateriManual').addEventListener('change', sinkronKelasManual);

$('#chatInput').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') { e.preventDefault(); kirimChat(); }
});

$('#modal').addEventListener('click', (e) => { if (e.target.id === 'modal') tutupModal(); });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') { tutupModal(); tutupSidebar(); } });

aturRoleUI();
$('#appView').style.display = 'none';
$('#loginView').style.display = 'grid';
pasangSemuaTilt();
pasangTilt($('.login-card'), 7);
geserSorot();
window.addEventListener('resize', geserSorot);
