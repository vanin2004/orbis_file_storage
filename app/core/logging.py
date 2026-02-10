"""
Настройка логирования приложения.
"""

from logging import Logger
from app.core.settings import settings

# Создание логгера с именем приложения
logging = Logger(settings.app_name)
