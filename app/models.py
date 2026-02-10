import datetime
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class FileMeta(Base):
    """
    SQLAlchemy модель для таблицы метаданных файлов.
    Хранит информацию о файлах, но не само содержимое.
    """

    __tablename__ = "file_meta"

    # Уникальный идентификатор файла (UUID)
    uuid: Mapped[str] = mapped_column(String, primary_key=True, index=True)

    # Имя файла (без расширения)
    filename: Mapped[str] = mapped_column(String, index=True)

    # Расширение файла (например, ".txt")
    file_extension: Mapped[str] = mapped_column(String, index=True)

    # Размер файла в байтах
    size: Mapped[int] = mapped_column(Integer)

    # Виртуальный путь или категория файла (определяет иерархию директорий)
    path: Mapped[str] = mapped_column(String, index=True)

    # Произвольный комментарий к файлу
    comment: Mapped[str | None] = mapped_column(String, nullable=True)

    # Дата и время создания файла (в UTC)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))

    # Дата и время последнего обновления метаданных файла
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
