from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.database import SessionLocal
from app.dependencies import require_siswa
from app.models.hasil import Hasil
from app.models.pengguna import Pengguna
from app.models.soal import Soal
from app.schemas.latihan import LatihanRequest


router = APIRouter(
    prefix="/api/latihan",
    tags=["Latihan"]
)


@router.post("")
def kerjakan_latihan(
    data: LatihanRequest,
    pengguna: Pengguna = Depends(require_siswa)
):

    kelas_siswa = (
        f"{pengguna.tingkat} {pengguna.rombel}"
    )

    with SessionLocal() as session:

        # =========================
        # AMBIL SOAL
        # =========================

        soal_ids = [
            item.soalId
            for item in data.jawaban
        ]

        hasil_soal = session.scalars(
            select(Soal).where(
                Soal.id.in_(soal_ids)
            )
        ).all()

        soal_map = {
            soal.id: soal
            for soal in hasil_soal
        }

        # =========================
        # VALIDASI SOAL
        # =========================

        for item in data.jawaban:

            soal = soal_map.get(
                item.soalId
            )

            if not soal:

                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"Soal dengan ID "
                        f"{item.soalId} "
                        f"tidak ditemukan"
                    )
                )

            # Siswa hanya boleh mengerjakan
            # soal untuk kelasnya.
            if kelas_siswa not in soal.kelas:

                raise HTTPException(
                    status_code=403,
                    detail=(
                        f"Soal dengan ID "
                        f"{item.soalId} "
                        f"bukan untuk kelas Anda"
                    )
                )

            # Pastikan pilihan jawaban valid.
            if (
                item.pilihan < 0
                or item.pilihan >= len(soal.opsi)
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Pilihan jawaban untuk "
                        f"soal {item.soalId} "
                        f"tidak valid"
                    )
                )

        # =========================
        # HITUNG NILAI
        # =========================

        benar = 0
        detail = []

        for item in data.jawaban:

            soal = soal_map[item.soalId]

            benar_soal = (
                item.pilihan == soal.jawaban
            )

            if benar_soal:
                benar += 1

            detail.append({
                "soalId": soal.id,
                "benar": benar_soal,
                "kunci": soal.jawaban
            })

        total = len(data.jawaban)

        nilai = (
            (benar / total) * 100
            if total > 0
            else 0
        )

        # =========================
        # SIMPAN HASIL
        # =========================

        hasil = Hasil(
            pengguna_id=pengguna.id,
            materi_id=data.materiId,
            nilai=nilai,
            benar=benar,
            total=total,
            detail=detail,
            dibuat_pada=datetime.now(
                timezone.utc
            )
        )

        session.add(hasil)

        session.commit()

        session.refresh(hasil)

        # =========================
        # RESPONSE
        # =========================

        return {
            "nilai": float(hasil.nilai),
            "benar": hasil.benar,
            "total": hasil.total,
            "detail": hasil.detail
        }