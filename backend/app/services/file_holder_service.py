from typing import Sequence
from app.repositories.file_repository import FileRepository
from app.repositories.file_meta_repository import FileMetaRepository
from app.schemas import FileCreate, FileUpdate
from app.models import FileMeta
from app.exceptions.service import (
    ServiceFileAlreadyExistsError,
    ServiceFileNotFoundError,
)
import uuid


class FileHolderService:
    """
    Сервис бизнес-логики для управления файлами.
    Оркестрирует работу с метаданными (БД) и физическим хранилищем файлов.
    """

    def __init__(
        self,
        file_repository: FileRepository,  # Репозиторий для работы с файлами
        file_meta_repository: FileMetaRepository,  # Репозиторий для работы с метаданными
    ):
        self._file_repository = file_repository
        self._file_meta_repository = file_meta_repository

    @staticmethod
    def _generate_file_path(
        file_id: uuid.UUID, file_extension: str
    ) -> str:  # file_id: UUID файла, file_extension: расширение
        """Генерирует уникальное имя файла для хранения на диске (UUID.ext)"""
        return f"{file_id}"

    async def create_file(
        self,
        file_data: bytes,  # Содержимое файла в байтах
        file_create: FileCreate,  # Метаданные для создания файла
    ) -> FileMeta:
        """
        Создает новый файл.
        Проверяет уникальность, сохраняет метаданные и содержимое.
        """

        if (
            await self._file_meta_repository.get_by_path_filename_extension(
                file_path=file_create.path,
                filename=file_create.filename,
                file_extension=file_create.file_extension,
            )
            is not None
        ):
            raise ServiceFileAlreadyExistsError(
                "File with the same path, filename and extension already exists"
            )

        file_id = uuid.uuid4()

        file_meta = await self._file_meta_repository.save(
            uuid=file_id,
            file_name=file_create.filename,
            file_extension=file_create.file_extension,
            file_path=file_create.path,
            size=file_create.size,
            comment=file_create.comment,
        )

        file_path = self._generate_file_path(file_id, file_create.file_extension)

        await self._file_repository.save(file_data, file_path)

        return file_meta

    async def get_file_meta(
        self, file_id: uuid.UUID
    ) -> FileMeta | None:  # file_id: UUID файла
        """Получает метаданные файла по ID"""

    async def get_file_by_id(self, file_id: uuid.UUID) -> bytes:  # file_id: UUID файла
        """Получает содержимое файла по ID"""
        file_meta = await self.get_file_meta(file_id)
        if file_meta is None:
            raise ServiceFileNotFoundError("File metadata not found")

        file_path = self._generate_file_path(
            uuid.UUID(file_meta.uuid), file_meta.file_extension
        )
        file_bytes = await self._file_repository.get(file_path)

        return file_bytes

    async def get_file_by_path_filename_extension(
        self,
        file_path: str,
        filename: str,
        file_extension: str,  # file_path: путь, filename: имя, file_extension: расширение
    ) -> bytes:
        """Получает содержимое файла по полному пути, имени и расширению"""
        file_meta = await self._file_meta_repository.get_by_path_filename_extension(
            file_path=file_path,
            filename=filename,
            file_extension=file_extension,
        )
        if file_meta is None:
            raise ServiceFileNotFoundError("File metadata not found")

        file_path = self._generate_file_path(
            uuid.UUID(file_meta.uuid), file_meta.file_extension
        )
        file_bytes = await self._file_repository.get(file_path)

        return file_bytes

    async def delete_file(
        self, file_id: uuid.UUID
    ) -> bool:  # file_id: UUID файла для удаления
        """Удаляет файл и его метаданные"""
        file_meta = await self.get_file_meta(file_id)
        if file_meta is None:
            raise ServiceFileNotFoundError("File metadata not found")

        file_path = self._generate_file_path(
            uuid.UUID(file_meta.uuid), file_meta.file_extension
        )

        await self._file_repository.delete(file_path)
        await self._file_meta_repository.delete(file_meta)

        return True

    async def list_files(self) -> Sequence[FileMeta]:
        return await self._file_meta_repository.list()

    async def search_files_by_path(
        self, path_prefix: str
    ) -> Sequence[FileMeta]:  # path_prefix: префикс пути для поиска
        """Ищет файлы по префиксу пути"""

        if len(path_prefix) == 0:
            return []
        if path_prefix[-1] != "/":
            path_prefix += "/"

        return await self._file_meta_repository.get_by_path_startswith(path_prefix)

    async def update_file_meta(
        self,
        file_id: uuid.UUID,
        update: FileUpdate,  # file_id: UUID файла, update: данные для обновления
    ) -> FileMeta:
        """Обновляет метаданные файла"""
        file_meta = await self.get_file_meta(file_id)
        if file_meta is None:
            raise ServiceFileNotFoundError("File metadata not found")

        data = update.model_dump(exclude_unset=True)
        if not data:
            return file_meta

        return await self._file_meta_repository.update(file_meta, data)

    async def sync_storage_with_db(self) -> None:
        """
        Синхронизирует физическое хранилище с базой данных.
        Удаляет файлы, которые есть в хранилище, но отсутствуют в БД.
        И удаляет метаданные файлов, которых нет в хранилище.
        """
        uuids = {
            file_meta.uuid for file_meta in await self._file_meta_repository.list()
        }
        await self._file_repository.delete_files_not_in_uuids(uuids)

    async def get_file_meta_by_full_path(self, file_path: str) -> FileMeta | None:
        return await self._file_meta_repository.get_by_full_path(file_path)
