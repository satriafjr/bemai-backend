from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.database import SessionLocal
from app.dependencies import get_current_user, require_guru
from app.models.materi import Materi
from app.models.pengguna import Pengguna
from app.schemas.materi import (
    MateriCreate,
    MateriUpdate
)


router = APIRouter(
    prefix="/api/materi",
    tags=["Materi"]
)


def materi_ke_dict(materi: Materi):
    return {
        "id": materi.id,
        "mapel": materi.mapel,
        "tingkat": materi.tingkat,
        "rombel": materi.rombel,
        "judul": materi.judul,
        "teks": materi.teks,
        "rangkuman": materi.rangkuman,
        "dibuatPada": materi.dibuat_pada.isoformat(),
        "diubahPada": materi.diubah_pada.isoformat()
    }


@router.get("")
def daftar_materi(
    pengguna: Pengguna = Depends(get_current_user)
):
    with SessionLocal() as session:

        query = select(Materi)

        if pengguna.peran == "siswa":
            query = query.where(
                Materi.tingkat == pengguna.tingkat
            )

            query = query.where(
                (Materi.rombel == [])
                | Materi.rombel.contains(
                    [pengguna.rombel]
                )
            )

        hasil = session.scalars(
            query.order_by(Materi.id)
        ).all()

        return [
            materi_ke_dict(materi)
            for materi in hasil
        ]


@router.get("/{materi_id}")
def detail_materi(
    materi_id: int,
    pengguna: Pengguna = Depends(get_current_user)
):
    with SessionLocal() as session:

        materi = session.get(
            Materi,
            materi_id
        )

        if not materi:
            raise HTTPException(
                status_code=404,
                detail="Materi tidak ditemukan"
            )

        if pengguna.peran == "siswa":

            if materi.tingkat != pengguna.tingkat:
                raise HTTPException(
                    status_code=403,
                    detail="Materi bukan untuk kelas Anda"
                )

            if (
                materi.rombel
                and pengguna.rombel not in materi.rombel
            ):
                raise HTTPException(
                    status_code=403,
                    detail="Materi bukan untuk rombel Anda"
                )

        return materi_ke_dict(materi)


@router.post("")
def tambah_materi(
    data: MateriCreate,
    pengguna: Pengguna = Depends(require_guru)
):
    sekarang = datetime.now(timezone.utc)

    materi = Materi(
        mapel=data.mapel,
        tingkat=data.tingkat,
        rombel=data.rombel,
        judul=data.judul,
        teks=data.teks,
        rangkuman=data.rangkuman,
        dibuat_pada=sekarang,
        diubah_pada=sekarang
    )

    with SessionLocal() as session:

        session.add(materi)
        session.commit()
        session.refresh(materi)

        return materi_ke_dict(materi)


@router.put("/{materi_id}")
def ubah_materi(
    materi_id: int,
    data: MateriUpdate,
    pengguna: Pengguna = Depends(require_guru)
):
    with SessionLocal() as session:

        materi = session.get(
            Materi,
            materi_id
        )

        if not materi:
            raise HTTPException(
                status_code=404,
                detail="Materi tidak ditemukan"
            )

        perubahan = data.model_dump(
            exclude_unset=True
        )

        for nama_field, nilai in perubahan.items():
            setattr(
                materi,
                nama_field,
                nilai
            )

        materi.diubah_pada = datetime.now(
            timezone.utc
        )

        session.commit()
        session.refresh(materi)

        return materi_ke_dict(materi)


@router.delete("/{materi_id}", status_code=204)
def hapus_materi(
    materi_id: int,
    pengguna: Pengguna = Depends(require_guru)
):
    with SessionLocal() as session:

        materi = session.get(
            Materi,
            materi_id
        )

        if not materi:
            raise HTTPException(
                status_code=404,
                detail="Materi tidak ditemukan"
            )

        session.delete(materi)
        session.commit()