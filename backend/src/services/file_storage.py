import aiofiles
import aiofiles.os
import os

from src.config import FsConfig


class LocalStorageError(Exception):
    """Базовый класс для ошибок локального хранилища."""

    pass


class LocalStorageUnavailableError(LocalStorageError):
    """Вызывается, когда локальное хранилище недоступно (например, диск полон, проблемы с правами)."""

    pass


class FileNotFoundError(LocalStorageError):
    """Вызывается, когда запрашиваемый файл не найден в хранилище."""

    pass


class FileWriteError(LocalStorageError):
    """Вызывается, когда запись файла в хранилище не удается."""

    pass


class AsyncFileService:
    """
    Асинхронная сессия для работы с файловой системой с поддержкой транзакций и блокировок.
    Реализует паттерн Unit of Work для файловых операций.
    """

    def __init__(
        self,
        config: FsConfig,
    ):
        """
        Инициализация асинхронной файловой сессии.

        Args:
            storage_path (str): путь к директории хранения файлов
            pending_prefix (str): префикс для временных файлов
        """

        self._storage_path = config.file_storage_path
        self._pending_files = set()
        os.makedirs(self._storage_path, exist_ok=True)

    async def set(self, file_bytes: bytes, file_name: str) -> None:
        """Запись файла в хранилище"""
        file_path = os.path.join(self._storage_path, file_name)
        try:
            async with aiofiles.open(file_path, "wb") as out_file:
                await out_file.write(file_bytes)
        except Exception as e:
            raise FileWriteError(f"Failed to write file '{file_name}': {e}")

    async def get(self, file_name: str) -> bytes:
        """
        Читает содержимое файла.

        Args:
            file_name (str): имя файла для чтения
        Returns:
            bytes: содержимое файла
        """
        try:
            async with aiofiles.open(
                os.path.join(self._storage_path, file_name), "rb"
            ) as in_file:
                return await in_file.read()
        except Exception:
            raise FileNotFoundError(f"File '{file_name}' not found in storage")

    async def delete(self, file_name: str) -> None:
        """
        Удаляет файл из хранилища.

        Args:
            file_name (str): имя файла для удаления
        Returns:
            bool: True если файл удалён
        """
        file_path = os.path.join(self._storage_path, file_name)
        try:
            await aiofiles.os.remove(file_path)
        except Exception:
            raise FileNotFoundError(f"File '{file_name}' not found in storage")

    async def list_files(self) -> list[str]:
        try:
            files = await aiofiles.os.listdir(self._storage_path)
        except Exception:
            raise LocalStorageUnavailableError("File storage is currently unavailable")
        return files

    async def is_exists(self, file_name: str) -> bool:
        """Проверяет существование файла"""
        try:
            return await aiofiles.os.path.exists(
                os.path.join(self._storage_path, file_name)
            )
        except Exception:
            raise LocalStorageUnavailableError("File storage is currently unavailable")
