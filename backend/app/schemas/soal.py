from pydantic import BaseModel, Field


class SoalBase(BaseModel):
    materiId: int | None = None
    topik: str | None = None
    tanya: str
    opsi: list[str] = Field(min_length=2)
    jawaban: int
    kelas: list[str] = Field(default_factory=list)


class SoalCreate(SoalBase):
    pass


class SoalUpdate(BaseModel):
    materiId: int | None = None
    topik: str | None = None
    tanya: str | None = None
    opsi: list[str] | None = None
    jawaban: int | None = None
    kelas: list[str] | None = None


class SoalGenerateRequest(BaseModel):
    materiId: int
    kelas: list[str] = Field(default_factory=list)


class SoalTerbitkanRequest(BaseModel):
    usulan: list[SoalBase] = Field(min_length=1)