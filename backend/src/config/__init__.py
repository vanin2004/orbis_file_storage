from .pg import PgConfig
from .fs import FsConfig

from src.settings import settings


pg_config = PgConfig(
    database_url=settings.database_url,
    retries=settings.db_retries,
    retry_delay_sec=settings.db_retry_delay,
    debug_mode=settings.debug,
)
fs_config = FsConfig(
    file_storage_path=settings.file_storage_path,
)


__all__ = ["PgConfig", "FsConfig", "pg_config", "fs_config"]
