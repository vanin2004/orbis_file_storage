from dataclasses import dataclass
from .config_base import ConfigBase


@dataclass
class FastAPIConfig(ConfigBase):
    host: str
    port: int
    log_level: str
    reload: bool
