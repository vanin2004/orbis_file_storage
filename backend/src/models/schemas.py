"""
Определение типов с валидацией.
Filename: 1-255 символов, буквы/цифры/._-.
FileExtension: 0-10 символов, буквы и цифры.
FilePath: 1-1024 символов, начинается и заканчивается на "/".
"""

from uuid import UUID
from typing import Annotated
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

Filename = Annotated[
    str, Field(min_length=1, max_length=255, pattern=r"^[a-zA-Z0-9._-]+$")
]
FileExtension = Annotated[
    str, Field(min_length=0, max_length=10, pattern=r"^[a-zA-Z0-9]+$")
]
FilePath = Annotated[
    str, Field(min_length=1, max_length=1024, pattern=r"^/[a-zA-Z0-9._/-]+/$")
]


class FileCreate(BaseModel):
    """Модель для создания записи о файле"""

    filename: Filename
    file_extension: FileExtension
    path: FilePath
    size: int
    comment: str | None = None


class FileRead(BaseModel):
    """Pydantic-модель метаданных файла для ответов API"""

    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    filename: str
    file_extension: str
    size: int
    path: str
    comment: str | None = None
    created_at: datetime
    updated_at: datetime | None = None


class FileUpdate(BaseModel):
    """Модель для обновления метаданных файла"""

    filename: Filename | None = None
    path: FilePath | None = None
    comment: str | None = None
    file_extension: FileExtension | None = None
