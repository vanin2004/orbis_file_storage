from uuid import UUID
from typing import Annotated
from pydantic import BaseModel, Field, field_validator

# Определение типов с валидацией
# Имя файла: от 1 до 255 символов, разрешены буквы, цифры, точки, подчеркивания и дефисы
Filename = Annotated[
    str, Field(min_length=1, max_length=255, pattern=r"^[a-zA-Z0-9._-]+$")
]
# Расширение файла: от 0 до 10 символов, только буквы и цифры
FileExtension = Annotated[
    str, Field(min_length=0, max_length=10, pattern=r"^[a-zA-Z0-9]+$")
]
# Путь к файлу (виртуальный): от 1 до 1024 символов
FilePath = Annotated[
    str, Field(min_length=1, max_length=1024, pattern=r"^[a-zA-Z0-9._/-]+$")
]


class FileCreate(BaseModel):
    """Модель для создания записи о файле"""

    filename: Filename
    file_extension: FileExtension
    path: FilePath
    size: int
    comment: str | None = None

    @field_validator("path")
    @classmethod
    def validate_path(cls, v):
        if not v.startswith("/") or not v.endswith("/"):
            raise ValueError("Путь должен начинаться и заканчиваться с /")
        return v


class FileRead(BaseModel):
    """Модель для чтения записи о файле (возвращается клиенту)"""

    id: UUID
    filename: str
    file_extension: str
    path: str
    size: int
    created_at: str
    updated_at: str | None = None
    comment: str | None = None


class FileUpdate(BaseModel):
    """Модель для обновления метаданных файла"""

    filename: Filename | None = None
    path: FilePath | None = None
    comment: str | None = None

    @field_validator("path")
    @classmethod
    def validate_path(cls, v):
        if v is not None and (not v.startswith("/") or not v.endswith("/")):
            raise ValueError("Путь должен начинаться и заканчиваться с /")
        return v
