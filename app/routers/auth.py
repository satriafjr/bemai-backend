import os

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from pwdlib import PasswordHash
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import select

from app.database import SessionLocal
from app.models.pengguna import Pengguna
from app.dependencies import get_current_user


router = APIRouter(
    prefix="/api/auth",
    tags=["Auth"]
)


password_hash = PasswordHash.recommended()


SESSION_SECRET = os.getenv("SESSION_SECRET")

if not SESSION_SECRET:
    raise RuntimeError("SESSION_SECRET belum diatur di file .env")


serializer = URLSafeTimedSerializer(SESSION_SECRET)


class LoginRequest(BaseModel):
    identitas: str
    kataSandi: str


@router.post("/login")
def login(
    data: LoginRequest,
    response: Response
):
    with SessionLocal() as session:

        pengguna = session.scalar(
            select(Pengguna).where(
                (Pengguna.email == data.identitas)
                | (Pengguna.nis == data.identitas)
            )
        )

        if not pengguna:
            raise HTTPException(
                status_code=401,
                detail="Identitas atau kata sandi salah"
            )

        if not password_hash.verify(
            data.kataSandi,
            pengguna.kata_sandi
        ):
            raise HTTPException(
                status_code=401,
                detail="Identitas atau kata sandi salah"
            )

        session_token = serializer.dumps({
            "pengguna_id": pengguna.id
        })

        response.set_cookie(
            key="bemai_session",
            value=session_token,
            httponly=True,
            samesite="lax",
            secure=False
        )

        return {
            "pengguna": {
                "id": pengguna.id,
                "nama": pengguna.nama,
                "peran": pengguna.peran,
                "email": pengguna.email,
                "nis": pengguna.nis,
                "tingkat": pengguna.tingkat,
                "rombel": pengguna.rombel
            }
        }


@router.get("/saya")
def saya(
    pengguna: Pengguna = Depends(get_current_user)
):
    return {
        "pengguna": {
            "id": pengguna.id,
            "nama": pengguna.nama,
            "peran": pengguna.peran,
            "email": pengguna.email,
            "nis": pengguna.nis,
            "tingkat": pengguna.tingkat,
            "rombel": pengguna.rombel
        }
    }


@router.post("/logout", status_code=204)
def logout(
    response: Response
):
    response.delete_cookie(
        key="bemai_session"
    )