from app.core.localstorage import AsyncFileSession


class FileRepository:
    """
    Репозиторий для работы с файловым хранилищем.
    Абстрагирует работу с AsyncFileSession.
    """

    def __init__(
        self, session: AsyncFileSession
    ):  # session: сессия файлового хранилища
        self._session = session

    async def save(
        self, file_data: bytes, file_name: str
    ) -> bool:  # file_data: содержимое файла, file_name: имя файла
        """Сохраняет данные файла (добавляет в сессию)"""
        await self._session.add(file_data, file_name)
        # flush и commit управляются извне (dependencies / service)
        await self._session.flush()
        # В localstorage.py, add только добавляет в pending dict.
        # flush записывает pending dict на диск с префиксом pending_.
        return True

    async def get(self, file_name: str) -> bytes:  # file_name: имя файла для чтения
        """Получает содержимое файла"""
        return await self._session.get(file_name)

    async def delete(self, file_name: str) -> bool:  # file_name: имя файла для удаления
        """Удаляет файл"""
        return await self._session.delete(file_name)

    async def list_files(self) -> list[str]:
        """Список файлов (без скрытых)"""
        return await self._session.list_files()

    async def list_all_files(self) -> list[str]:
        """Полный список файлов"""
        return await self._session.list_all_files()

    async def is_exists(self, file_name: str) -> bool:
        """Проверка существования"""
        return await self._session.is_exists(file_name)

    async def delete_files_not_in_uuids(
        self, uuids: set[str]
    ) -> None:  # uuids: множество допустимых UUID файлов
        """Удаляет файлы, которых нет в переданном множестве UUID"""
        files = await self._session.list_files()
        for file in files:
            if file not in uuids:
                await self.delete(file)
