from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.database import SessionLocal
from app.dependencies import get_current_user, require_guru
from app.models.materi import Materi
from app.models.pengguna import Pengguna
from app.models.soal import Soal
from app.schemas.soal import (
    SoalCreate,
    SoalGenerateRequest,
    SoalTerbitkanRequest
)


router = APIRouter(
    prefix="/api/soal",
    tags=["Soal"]
)


# =========================
# HELPER
# =========================

def soal_ke_dict(soal: Soal):
    return {
        "id": soal.id,
        "materiId": soal.materi_id,
        "topik": soal.topik,
        "tanya": soal.tanya,
        "opsi": soal.opsi,
        "jawaban": soal.jawaban,
        "kelas": soal.kelas,
        "dibuatPada": soal.dibuat_pada.isoformat()
    }


# =========================
# GET DAFTAR SOAL
# =========================

@router.get("")
def daftar_soal(
    pengguna: Pengguna = Depends(get_current_user)
):
    with SessionLocal() as session:

        query = select(Soal)

        # Siswa hanya boleh melihat
        # soal untuk kelasnya sendiri.
        if pengguna.peran == "siswa":

            kelas_siswa = (
                f"{pengguna.tingkat} {pengguna.rombel}"
            )

            query = query.where(
                Soal.kelas.contains([kelas_siswa])
            )

        hasil = session.scalars(
            query.order_by(Soal.id)
        ).all()

        return [
            soal_ke_dict(soal)
            for soal in hasil
        ]


# =========================
# GET DETAIL SOAL
# =========================

@router.get("/{soal_id}")
def detail_soal(
    soal_id: int,
    pengguna: Pengguna = Depends(get_current_user)
):
    with SessionLocal() as session:

        soal = session.get(
            Soal,
            soal_id
        )

        if not soal:
            raise HTTPException(
                status_code=404,
                detail="Soal tidak ditemukan"
            )

        # Siswa hanya boleh membuka
        # soal yang ditujukan untuk kelasnya.
        if pengguna.peran == "siswa":

            kelas_siswa = (
                f"{pengguna.tingkat} {pengguna.rombel}"
            )

            if kelas_siswa not in soal.kelas:

                raise HTTPException(
                    status_code=403,
                    detail="Soal bukan untuk kelas Anda"
                )

        return soal_ke_dict(soal)


# =========================
# TAMBAH SOAL MANUAL
# =========================

@router.post("")
def tambah_soal(
    data: SoalCreate,
    pengguna: Pengguna = Depends(require_guru)
):

    # Jika materiId diberikan,
    # pastikan materi tersebut ada.
    if data.materiId is not None:

        with SessionLocal() as session:

            materi = session.get(
                Materi,
                data.materiId
            )

            if not materi:

                raise HTTPException(
                    status_code=404,
                    detail="Materi tidak ditemukan"
                )

    # Pastikan indeks jawaban benar.
    #
    # Contoh:
    # opsi = ["A", "B", "C", "D"]
    # jawaban = 0 -> A
    # jawaban = 1 -> B
    # dan seterusnya.
    if (
        data.jawaban < 0
        or data.jawaban >= len(data.opsi)
    ):

        raise HTTPException(
            status_code=400,
            detail="Indeks jawaban tidak valid"
        )

    sekarang = datetime.now(timezone.utc)

    soal = Soal(
        materi_id=data.materiId,
        topik=data.topik,
        tanya=data.tanya,
        opsi=data.opsi,
        jawaban=data.jawaban,
        kelas=data.kelas,
        dibuat_pada=sekarang
    )

    with SessionLocal() as session:

        session.add(soal)

        session.commit()

        session.refresh(soal)

        return soal_ke_dict(soal)


# =========================
# GENERATE SOAL
# =========================

@router.post("/generate")
def generate_soal(
    data: SoalGenerateRequest,
    pengguna: Pengguna = Depends(require_guru)
):

    with SessionLocal() as session:

        # Cari materi berdasarkan ID.
        materi = session.get(
            Materi,
            data.materiId
        )

        if not materi:

            raise HTTPException(
                status_code=404,
                detail="Materi tidak ditemukan"
            )

        # Materi harus memiliki isi.
        if not materi.teks and not materi.rangkuman:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Materi belum memiliki isi "
                    "untuk dibuat menjadi soal"
                )
            )

        # =========================
        # MENENTUKAN KELAS
        # =========================

        kelas = data.kelas

        # Jika kelas tidak dikirim,
        # gunakan rombel dari materi.
        if not kelas:

            kelas = [
                f"{materi.tingkat} {rombel}"
                for rombel in materi.rombel
            ]

        # Jika rombel materi kosong,
        # berarti materi berlaku untuk
        # semua rombel pada tingkat tersebut.
        if not kelas:

            kelas = [
                f"{materi.tingkat} A",
                f"{materi.tingkat} B",
                f"{materi.tingkat} C",
                f"{materi.tingkat} D",
                f"{materi.tingkat} E",
                f"{materi.tingkat} F"
            ]

        # =========================
        # MENGAMBIL SUMBER MATERI
        # =========================

        sumber = (
            materi.teks
            + materi.rangkuman
        )

        usulan = []

        # =========================
        # SOAL 1
        # =========================

        if len(sumber) >= 1:

            usulan.append({
                "materiId": materi.id,
                "topik": materi.judul,
                "tanya": (
                    f"Berdasarkan materi "
                    f"'{materi.judul}', "
                    f"manakah pernyataan yang "
                    f"paling sesuai?"
                ),
                "opsi": [
                    sumber[0],
                    (
                        "Pernyataan tersebut "
                        "tidak berhubungan "
                        "dengan materi."
                    ),
                    (
                        "Materi tersebut hanya "
                        "membahas bagian lain."
                    ),
                    (
                        "Pernyataan tersebut "
                        "merupakan informasi "
                        "yang salah."
                    )
                ],
                "jawaban": 0,
                "kelas": kelas
            })

        # =========================
        # SOAL 2
        # =========================

        if len(sumber) >= 2:

            usulan.append({
                "materiId": materi.id,
                "topik": materi.judul,
                "tanya": (
                    f"Apa informasi penting "
                    f"yang terdapat dalam "
                    f"materi '{materi.judul}'?"
                ),
                "opsi": [
                    sumber[1],
                    (
                        "Tidak ada informasi "
                        "penting dalam materi."
                    ),
                    (
                        "Materi hanya berisi "
                        "contoh tanpa penjelasan."
                    ),
                    (
                        "Materi tidak berhubungan "
                        "dengan topik pembelajaran."
                    )
                ],
                "jawaban": 0,
                "kelas": kelas
            })

        return {
            "usulan": usulan
        }


# =========================
# TERBITKAN SOAL
# =========================

@router.post("/terbitkan")
def terbitkan_soal(
    data: SoalTerbitkanRequest,
    pengguna: Pengguna = Depends(require_guru)
):

    sekarang = datetime.now(timezone.utc)

    soal_tersimpan = []

    with SessionLocal() as session:

        # Periksa setiap soal yang akan diterbitkan.
        for item in data.usulan:

            # =========================
            # VALIDASI MATERI
            # =========================

            if item.materiId is not None:

                materi = session.get(
                    Materi,
                    item.materiId
                )

                if not materi:

                    raise HTTPException(
                        status_code=404,
                        detail=(
                            f"Materi dengan ID "
                            f"{item.materiId} "
                            f"tidak ditemukan"
                        )
                    )

            # =========================
            # VALIDASI JAWABAN
            # =========================

            if (
                item.jawaban < 0
                or item.jawaban >= len(item.opsi)
            ):

                raise HTTPException(
                    status_code=400,
                    detail="Indeks jawaban tidak valid"
                )

            # =========================
            # BUAT SOAL
            # =========================

            soal = Soal(
                materi_id=item.materiId,
                topik=item.topik,
                tanya=item.tanya,
                opsi=item.opsi,
                jawaban=item.jawaban,
                kelas=item.kelas,
                dibuat_pada=sekarang
            )

            session.add(soal)

            soal_tersimpan.append(soal)

        # Simpan semua soal sekaligus.
        session.commit()

        # Ambil ID yang sudah dibuat database.
        for soal in soal_tersimpan:

            session.refresh(soal)

        return {
            "soal": [
                soal_ke_dict(soal)
                for soal in soal_tersimpan
            ]
        }


# =========================
# HAPUS SOAL
# =========================

@router.delete("/{soal_id}", status_code=204)
def hapus_soal(
    soal_id: int,
    pengguna: Pengguna = Depends(require_guru)
):
    with SessionLocal() as session:

        soal = session.get(
            Soal,
            soal_id
        )

        if not soal:

            raise HTTPException(
                status_code=404,
                detail="Soal tidak ditemukan"
            )

        session.delete(soal)

        session.commit()