import os


# Базовые настройки приложения
class Config:
    RIOT_API = os.environ.get('RIOT_API')
    API_VERSION = os.environ.get('API_VERSION')
