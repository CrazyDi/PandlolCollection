import os


# Базовые настройки приложения
class Config:
    RIOT_API = os.environ.get('RIOT_API')
