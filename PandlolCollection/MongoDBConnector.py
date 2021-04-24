from datetime import datetime

from pymongo import MongoClient, InsertOne
from pymongo.errors import BulkWriteError, PyMongoError


class MongoDBConnector:
    """
    Класс доступа к MongoDB
    """
    def __init__(self, host: str = 'localhost', port: int = 27017):
        self._client = MongoClient(host, port)
        self.db = self._client.pandlol

    def insert_record(self, table_name: str, record):
        """
        Добавление записи в таблицу
        :param table_name: Название таблицы
        :param record: Запись
        :return: Номер записи, если
        """
        try:
            table = self.db[table_name]

            inserted_id = table.insert_one(record).inserted_id
            return {'status': 'OK', 'result': inserted_id}
        except PyMongoError:
            return {'status': 'ERROR', 'error': PyMongoError}

    def read_record(self, table_name: str, record):
        """
        Поиск записи в таблице
        :param table_name: Название таблицы
        :param record: Запись, которую ищем
        :return: Результат поиска
        """
        try:
            table = self.db[table_name]

            found_record = table.find_one(record)

            return {'status': 'OK', 'result': found_record}
        except PyMongoError:
            return {'status': 'ERROR', 'error': PyMongoError}

    def close_connection(self):
        self._client.close()
