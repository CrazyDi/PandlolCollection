from pymongo import MongoClient


class MongoDBConnector:
    """
    Класс доступа к MongoDB
    """
    def __init__(self, host: str = 'localhost', port: int = 27017):
        self._client = MongoClient(host, port)
        self.db = self._client.pandlol

    def write_data(self):
        pass

    def read_data(self):
        pass
