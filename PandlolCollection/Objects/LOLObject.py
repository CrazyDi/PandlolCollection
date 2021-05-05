import requests

from pymongo import MongoClient
from pymongo.errors import PyMongoError, ConnectionFailure
from time import sleep
from typing import Dict, List

from config import Config
from PandlolCollection.constant import REGION, PLATFORM_REGION, PLATFORM


class LOLObject:
    """
    Базовый класс моего объекта для загрузки данных
    """
    def __init__(
            self,
            connection: MongoClient = None,
            record: Dict = None,
            table_name: str = "",
            find_field: List = None,
            update_field: List = None
    ):
        """
        Конструктор
        :param connection: Коннект к NOSQL БД
        :param table_name: Наименование таблицы
        :param record: Словарь с записью объекта
        :param find_field: Поля для поиска
        :param update_field: Поля для записи
        """
        if connection:
            self.__database = connection.get_database(Config.DATABASE)
            self.__table = self.__database[table_name]
        else:
            self.__database = None
            self.__table = None

        if record:
            self._record = record
        else:
            self._record = {}

        self.__find_field = find_field
        self.__update_field = update_field

    @staticmethod
    def get_request(
            platform: str,
            api: str,
            version: str,
            api_type: str,
            **url_params
    ) -> Dict:
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

    @property
    def __find_record(self) -> Dict:
        """
        Запись для поиска
        """
        record = {}

        if self.__find_field:
            for f in self.__find_field:
                record[f] = self._record[f]

        return record

    @property
    def __update_record(self) -> Dict:
        """
        Запись для обновления
        """
        record = {}

        if self.__update_field:
            for f in self.__update_field:
                record[f] = self._record[f]

        return record

    def read_one(self) -> Dict:
        """
        Метод ищет первуб запись, удовлетворяющую условиям
        :return: Результат
        """
        try:
            if self.__database:
                found_record = self.__table.find_one(self.__find_record)

                return {'status': 'OK', 'result': found_record}
            else:
                raise ConnectionFailure
        except PyMongoError:
            return {'status': 'ERROR', 'error': PyMongoError}

    def insert(self) -> Dict:
        """
        Метод добавления записи в таблицу NOSQL БД
        """
        try:
            if self.__database:
                inserted_result = self.__table.insert_one(self._record)
                return {'status': 'OK', 'result': inserted_result}
            else:
                raise ConnectionFailure
        except PyMongoError:
            return {'status': 'ERROR', 'error': PyMongoError}

    def update(self) -> Dict:
        """
        Метод изменения записи
        """
        try:
            if self.__database:
                updated_result = self.__table.update_one(self.__find_record, {'$set': self.__update_record})

                return {'status': 'OK', 'result': updated_result}
            else:
                raise ConnectionFailure
        except PyMongoError:
            return {'status': 'ERROR', 'error': PyMongoError}

    def delete(self) -> Dict:
        """
        Метод удаления записей
        """
        try:
            if self.__database:
                deleted_result = self.__table.delete_many(self.__find_record)

                return {'status': 'OK', 'result': deleted_result}
            else:
                raise ConnectionFailure
        except PyMongoError:
            return {'status': 'ERROR', 'error': PyMongoError}
