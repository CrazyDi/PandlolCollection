import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


# Базовые настройки приложения
class Config:
    # path = os.
    RIOT_API = os.environ.get('RIOT_API', '1')
    API_VERSION = os.environ.get('API_VERSION', '2')
