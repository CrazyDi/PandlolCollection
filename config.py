import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


# Базовые настройки приложения
class Config:
    RIOT_API = os.environ.get('RIOT_API', '1')
    SQL_CONNECTION_STRING = os.environ.get('SQL_CONNECTION_STRING', 'sqlite:///data.db')
    NOSQL_CONNECTION_STRING = os.environ.get('NOSQL_CONNECTION_STRING', "mongodb://localhost:27017/")
    DATABASE = os.environ.get('DATABASE', 'pandlol')
