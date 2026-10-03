from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.database import test_database_connection
from app.routers import auth
from app.routers import materi
from app.routers import soal
from app.routers import latihan


app = FastAPI(
    title="Bemai Backend"
)


# =========================
# ROUTER
# =========================

app.include_router(auth.router)
app.include_router(materi.router)
app.include_router(soal.router)
app.include_router(latihan.router)


# =========================
# ERROR HANDLER
# =========================

@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException
):
    kode_status = {
        400: "BAD_REQUEST",
        401: "TIDAK_LOGIN",
        403: "AKSES_DITOLAK",
        404: "TIDAK_DITEMUKAN",
        409: "KONFLIK",
        500: "SERVER_ERROR",
        502: "AI_ERROR",
    }

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "kode": kode_status.get(
                    exc.status_code,
                    "ERROR"
                ),
                "pesan": str(exc.detail)
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "kode": "BAD_REQUEST",
                "pesan": "Data yang dikirim tidak valid"
            }
        }
    )


# =========================
# HEALTH CHECK
# =========================

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "waktu": datetime.now(
            timezone.utc
        ).isoformat().replace(
            "+00:00",
            "Z"
        )
    }


@app.get("/api/health/db")
def database_health_check():

    test_database_connection()

    return {
        "status": "ok",
        "database": "connected"
    }