import requests
from time import sleep

from config import Config
from PandlolCollection.constant import PLATFORM


class RIOTConnector:
    """
    Класс доступа к RIOT API
    """
    def __init__(self, platform: str, api: str, api_type: str, **url_params):
        """
        Инициализация запроса
        :param platform: Платформа (константа PLATFORM)
        :param api: Название API
        :param api_type: Тип API
        :param url_params: Параметры запроса
        """
        platform_name = PLATFORM[platform]

        self.url = f'https://{platform_name}/lol/{api}/{Config.API_VERSION}/{api_type}'

        if url_params.get('path_params') is not None:
            for param in url_params['path_params']:
                self.url += '/' + url_params['path_params'][param]

        if url_params.get('query_params') is not None:
            self.url += '?'
            for param in url_params['query_params']:
                self.url += f'{param}={url_params["query_params"][param]}'

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,be;q=0.6",
            "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://developer.riotgames.com",
            "X-Riot-Token": Config.RIOT_API
        }

    def get_request(self):
        """
        Метод осуществляет запрос к RIOT API и возвращает результат
        """
        sleep(1.2)
        try:
            response = requests.get(url=self.url, headers=self.headers)

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
