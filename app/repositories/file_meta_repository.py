from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, case
from sqlalchemy.exc import SQLAlchemyError
from typing import Sequence
import datetime

from uuid import UUID
from app.models import FileMeta
from app.exceptions.database import DatabaseOperationError


class FileMetaRepository:
    """
    Репозиторий для работы с метаданными файлов в БД.
    """

    def __init__(self, session: AsyncSession):  # session: асинхронная сессия БД
        self._session = session

    @staticmethod
    def _apply_pagination(
        stmt, limit: int | None, offset: int
    ):  # stmt: SQL запрос, limit: максимум записей, offset: смещение
        """Применяет пагинацию к запросу"""
        stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        return stmt

    async def save(
        self,
        uuid: UUID,  # Уникальный идентификатор файла
        file_name: str,  # Имя файла без расширения
        file_extension: str,  # Расширение файла
        file_path: str,  # Путь расположения файла
        size: int,  # Размер файла в байтах
        comment: str | None = None,  # Комментарий к файлу
    ) -> FileMeta:
        """Сохраняет новую запись о файле"""

        created_at = datetime.datetime.now(datetime.timezone.utc)

        file_meta = FileMeta(
            uuid=str(uuid),
            filename=file_name,
            file_extension=file_extension,
            path=file_path,
            size=size,
            comment=comment,
            created_at=created_at,
            updated_at=None,
        )

        try:
            self._session.add(file_meta)
            await self._session.flush()

            return file_meta
        except SQLAlchemyError as e:
            raise DatabaseOperationError(f"Error saving file metadata: {e}")

    async def get_by_id(
        self, file_id: UUID | str, limit: int | None = 1, offset: int = 0
    ) -> FileMeta | None:
        """Поиск по UUID"""
        try:
            stmt = select(FileMeta).where(FileMeta.uuid == str(file_id))
            stmt = self._apply_pagination(stmt, limit, offset)
            result = await self._session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseOperationError(f"Error retrieving file metadata by ID: {e}")

    async def get_by_path_filename_extension(
        self,
        file_path: str,
        filename: str,
        file_extension: str,
        limit: int | None = 1,
        offset: int = 0,
    ) -> FileMeta | None:
        try:
            stmt = select(FileMeta).where(
                FileMeta.path == file_path,
                FileMeta.filename == filename,
                FileMeta.file_extension == file_extension,
            )
            stmt = self._apply_pagination(stmt, limit, offset)
            result = await self._session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseOperationError(
                f"Error retrieving file metadata by path info: {e}"
            )

    async def get_by_path(
        self, file_path: str, limit: int | None = None, offset: int = 0
    ) -> Sequence[FileMeta]:
        try:
            stmt = select(FileMeta).where(FileMeta.path == file_path)
            stmt = self._apply_pagination(stmt, limit, offset)
            result = await self._session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise DatabaseOperationError(f"Error retrieving files by path: {e}")

    async def get_by_word_in_path(
        self, word: str, limit: int | None = None, offset: int = 0
    ) -> Sequence[FileMeta]:
        try:
            stmt = select(FileMeta).where(FileMeta.path.contains(word))
            stmt = self._apply_pagination(stmt, limit, offset)
            result = await self._session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise DatabaseOperationError(f"Error retrieving files by word in path: {e}")

    async def get_by_path_startswith(
        self, word: str, limit: int | None = None, offset: int = 0
    ) -> Sequence[FileMeta]:
        try:
            stmt = select(FileMeta).where(FileMeta.path.startswith(word))
            stmt = self._apply_pagination(stmt, limit, offset)
            result = await self._session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise DatabaseOperationError(
                f"Error retrieving files by path startswith: {e}"
            )

    async def list(
        self, limit: int | None = None, offset: int = 0
    ) -> Sequence[FileMeta]:
        try:
            stmt = self._apply_pagination(select(FileMeta), limit, offset)
            result = await self._session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise DatabaseOperationError(f"Error listing files: {e}")

    async def delete(self, file_meta: FileMeta) -> bool:
        try:
            await self._session.delete(file_meta)
            return True
        except SQLAlchemyError as e:
            raise DatabaseOperationError(f"Error deleting file metadata: {e}")

    async def delete_many(self, file_metas: Sequence[FileMeta]) -> bool:
        if not file_metas:
            return False

        uuids = [str(file_meta.uuid) for file_meta in file_metas]
        try:
            result = await self._session.execute(
                delete(FileMeta)
                .where(FileMeta.uuid.in_(uuids))
                .returning(FileMeta.uuid)
            )
            return result.first() is not None
        except SQLAlchemyError as e:
            raise DatabaseOperationError(f"Error deleting multiple file metadata: {e}")

    async def update(self, file_meta: FileMeta, data: dict) -> FileMeta:
        try:
            for key, value in data.items():
                setattr(file_meta, key, value)
            file_meta.updated_at = datetime.datetime.now(datetime.timezone.utc)
            await self._session.flush()
            return file_meta
        except SQLAlchemyError as e:
            raise DatabaseOperationError(f"Error updating file metadata: {e}")

    async def get_by_full_path(self, full_path: str) -> FileMeta | None:
        """
        Получает метаданные файла по полному пути.
        """
        try:
            stmt = select(FileMeta).where(
                func.concat(
                    FileMeta.path,
                    FileMeta.filename,
                    case(
                        (FileMeta.file_extension != "", "." + FileMeta.file_extension),
                        else_="",
                    ),
                )
                == full_path
            )
            result = await self._session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseOperationError(f"Error retrieving file by full path: {e}")
