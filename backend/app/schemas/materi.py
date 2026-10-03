from pydantic import BaseModel, Field


class MateriBase(BaseModel):
    mapel: str
    tingkat: str
    rombel: list[str] = Field(default_factory=list)
    judul: str
    teks: list[str] = Field(default_factory=list)
    rangkuman: list[str] = Field(default_factory=list)


class MateriCreate(MateriBase):
    pass


class MateriUpdate(BaseModel):
    mapel: str | None = None
    tingkat: str | None = None
    rombel: list[str] | None = None
    judul: str | None = None
    teks: list[str] | None = None
    rangkuman: list[str] | None = None


class MateriResponse(MateriBase):
    id: int
    dibuat_pada: str
    diubah_pada: str