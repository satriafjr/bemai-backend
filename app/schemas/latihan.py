from pydantic import BaseModel, Field


class JawabanLatihan(BaseModel):
    soalId: int
    pilihan: int


class LatihanRequest(BaseModel):
    materiId: int | None = None
    jawaban: list[JawabanLatihan] = Field(
        min_length=1
    )