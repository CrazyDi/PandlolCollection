from pymongo import MongoClient, InsertOne, ReplaceOne
from pymongo.errors import BulkWriteError


class MongoDBConnector:
    """
    Класс доступа к MongoDB
    """
    def __init__(self, host: str = 'localhost', port: int = 27017):
        self._client = MongoClient(host, port)
        self.db = self._client.pandlol

    def write_data(self, table_name: str, data, default_fields, filter_columns, value_columns):
        """
        Метод записывает данные в таблицу по условию.
        Если данные по фильтру найдена, они перезаписываются, если нет - добавляются
        :param table_name: Наименование таблицы
        :param data: Данные
        :param filter_columns: Колонки фильтра
        :param value_columns: Колонки данных
        :return: Результат выполнения операции
        """
        table = self.db[table_name]
        records = []

        for record in data:
            filter_record = default_fields.copy()
            value_record = default_fields.copy()
            for filter_column in filter_columns:
                filter_record[filter_column] = record[filter_column]
                value_record[filter_column] = record[filter_column]

            for value_column in value_columns:
                value_record[value_column] = record[value_column]

            records.append(InsertOne(value_record))
            # records.append(ReplaceOne(filter_record, value_record, upsert=True))

        try:
            if len(records) > 0:
                result = table.bulk_write(records)

                return result.bulk_api_result
        except BulkWriteError as bwe:
            return bwe.details

    def read_data(self):
        pass

    def close_connection(self):
        self._client.close()
