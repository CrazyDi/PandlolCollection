import requests

from pymongo import MongoClient
from pymongo.errors import PyMongoError, ConnectionFailure
from time import sleep
from typing import Dict

from config import Config
from PandlolCollection.constant import REGION, PLATFORM_REGION, PLATFORM


class LOLObject:
    """
    Базовый класс моего объекта для загрузки данных
    """
    def __init__(
            self,
            connection: MongoClient = None,
            record: Dict = None
    ):
        """
        Конструктор
        :param nosql_connection: Коннект к NOSQL БД
        :param sql_connection: Коннект к SQL БД
        :param record: Словарь с записью объекта
        """
        if connection:
            self.__database = connection.get_database(Config.DATABASE)
        else:
            self.__database = None

        if record:
            self._record = record
        else:
            self._record = {}

    @staticmethod
    def get_request(
            platform: str,
            api: str,
            version: str,
            api_type: str,
            **url_params
    ):
        """
        Метод получения данных из RIOT API
        :param platform: Платформа
        :param api: Название API
        :param version: Версия API
        :param api_type: Тип API
        :param url_params: Параметры. path_params - для параметров в url, query_params - для параметров в запрос
        :return:
        """
        # Костыль для API match-v5
        if version == 'v5':
            platform_name = REGION[PLATFORM_REGION[platform]]
        else:
            platform_name = PLATFORM[platform]

        # Формируем url
        url = f'https://{platform_name}/lol/{api}/{version}/{api_type}'

        # Добавляем параметры в url
        if url_params.get('path_params') is not None:
            for param in url_params['path_params']:
                url += '/' + url_params['path_params'][param]

        # Добавляем тип параметров в запрос
        if url_params.get('type_params') is not None:
            url += '/' + url_params['type_params']

        # Добавляем параметры в запрос
        if url_params.get('query_params') is not None:
            url += '?'
            for param in url_params['query_params']:
                url += f'{param}={url_params["query_params"][param]}' + '&'
            url = url.rstrip('&')

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,be;q=0.6",
            "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://developer.riotgames.com",
            "X-Riot-Token": Config.RIOT_API
        }

        # Осуществляем сам запрос
        sleep(1.2)
        try:
            response = requests.get(url=url, headers=headers)

            if response.status_code == 200:
                return {
                    "status": "OK",
                    "data": response.json()
                }
            else:
                return {
                    "status": "error",
                    "error":
                        {
                            "type": "response_error",
                            "code": response.status_code
                        }
                }
        except requests.RequestException as err:
            return {
                "status": "error",
                "error":
                    {
                        "type": "internal_error",
                        "code": err.errno,
                        "error_name": err.strerror
                    }
            }

    def _insert(self, table_name: str, record: Dict):
        """
        Метод добавления записи в таблицу NOSQL БД
        :param table_name: Имя таблицы
        :param record: Запись для добавления
        :return: Результат
        """
        try:
            if self.__database:
                table = self.__database[table_name]

                inserted_id = table.insert_one(record).inserted_id
                return {'status': 'OK', 'result': inserted_id}
            else:
                raise ConnectionFailure
        except PyMongoError:
            return {'status': 'ERROR', 'error': PyMongoError}

    def _read_one(self, table_name: str, record: Dict):
        """
        Метод ищет первуб запись, удовлетворяющую поданным условиям
        :param table_name: Имя таблицы
        :param record: Условия поиска
        :return: Результат
        """
        try:
            if self.__database:
                table = self.__database[table_name]

                found_record = table.find_one(record)

                return {'status': 'OK', 'result': found_record}
            else:
                raise ConnectionFailure
        except PyMongoError:
            return {'status': 'ERROR', 'error': PyMongoError}

    def _update(self, table_name, record_to_find, record_to_update):
        """
        Метод изменения записи
        :param table_name: Таблица
        :param record_to_find: Запись, которую надо переписать
        :param record_to_update: Поля, которые надо обновить
        :return: Результат
        """
        try:
            if self.__database:
                table = self.__database[table_name]

                result = table.update_one(record_to_find, {'$set': record_to_update}, upsert=True)

                return {'status': 'OK', 'result': result}
            else:
                raise ConnectionFailure
        except PyMongoError:
            return {'status': 'ERROR', 'error': PyMongoError}

    def _nosql_delete(self, table_name, record_to_delete):
        """
        Метод удаления записей
        :param table_name:
        :param record_to_delete:
        :return:
        """
        try:
            if self.__database:
                table = self.__database[table_name]

                result = table.delete_many(record_to_delete)

                return {'status': 'OK', 'result': result}
            else:
                raise ConnectionFailure
        except PyMongoError:
            return {'status': 'ERROR', 'error': PyMongoError}
