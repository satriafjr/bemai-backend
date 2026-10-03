from datetime import datetime

from sqlalchemy import BigInteger, String, Text, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Materi(Base):
    __tablename__ = "materi"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    mapel: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    tingkat: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    rombel: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list
    )

    judul: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    teks: Mapped[list[str]] = mapped_column(
        ARRAY(Text),
        nullable=False,
        default=list
    )

    rangkuman: Mapped[list[str]] = mapped_column(
        ARRAY(Text),
        nullable=False,
        default=list
    )

    dibuat_pada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    diubah_pada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )