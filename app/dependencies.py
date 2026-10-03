import os

from fastapi import Depends, HTTPException, Request
from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.pengguna import Pengguna


load_dotenv()


SESSION_SECRET = os.getenv("SESSION_SECRET")

if not SESSION_SECRET:
    raise RuntimeError(
        "SESSION_SECRET belum diatur di file .env"
    )


serializer = URLSafeTimedSerializer(
    SESSION_SECRET
)


def get_current_user(
    request: Request
) -> Pengguna:

    session_token = request.cookies.get(
        "bemai_session"
    )

    if not session_token:
        raise HTTPException(
            status_code=401,
            detail="Belum login"
        )

    try:
        data = serializer.loads(
            session_token,
            max_age=86400
        )

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Session tidak valid atau sudah kedaluwarsa"
        )

    with SessionLocal() as session:

        pengguna = session.get(
            Pengguna,
            data["pengguna_id"]
        )

        if not pengguna:
            raise HTTPException(
                status_code=401,
                detail="Pengguna tidak ditemukan"
            )

        return pengguna


def require_guru(
    pengguna: Pengguna = Depends(
        get_current_user
    )
) -> Pengguna:

    if pengguna.peran != "guru":
        raise HTTPException(
            status_code=403,
            detail="Akses hanya untuk guru"
        )

    return pengguna


def require_siswa(
    pengguna: Pengguna = Depends(
        get_current_user
    )
) -> Pengguna:

    if pengguna.peran != "siswa":
        raise HTTPException(
            status_code=403,
            detail="Akses hanya untuk siswa"
        )

    return pengguna