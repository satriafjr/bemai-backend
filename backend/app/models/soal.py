from datetime import datetime

from sqlalchemy import BigInteger, String, Text, DateTime, Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Soal(Base):
    __tablename__ = "soal"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    materi_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True
    )

    topik: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    tanya: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    opsi: Mapped[list[str]] = mapped_column(
        ARRAY(Text),
        nullable=False
    )

    jawaban: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    kelas: Mapped[list[str]] = mapped_column(
        ARRAY(Text),
        nullable=False
    )

    dibuat_pada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )