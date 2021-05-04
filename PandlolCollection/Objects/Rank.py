import random

from typing import Dict, List

from PandlolCollection.constant import QUEUE, TIER, DIVISION, LEAGUE
from PandlolCollection.Objects.LOLObject import LOLObject


class Rank(LOLObject):
    """
    Объект ранга
    """
    @property
    def platform(self) -> str:
        return self._record.get('platform')

    @property
    def queue(self) -> int:
        return self._record.get('queue', 0)

    @property
    def tier(self) -> int:
        return self._record.get('tier', 0)

    @property
    def division(self) -> int:
        return self._record.get('division', 0)

    def get_max_page(self) -> Dict:
        """
        Возвращает максимальную страницу из базы
        """
        result = {
            "max_page": 100,
            "delta": 50
        }

        result_page = self._read_one(
            table_name='page_list',
            record={
                'platform': self.platform,
                'tier': self.tier,
                'division': self.division,
                'queue': self.queue
            }
        )

        if result_page['status'] == 'OK' and result_page.get('result'):
            result['max_page'] = result_page['result'].get('max_page')
            result['delta'] = 10

        return result

    def riot_get_page_len(self, page_num: int) -> int:
        """
        Получает кол-во призывателей на заданной странице
        :param page_num: номер страницы
        :return: Кол-во призывателей
        """
        result = 0

        page_result = self.get_request(
            self.platform,
            'league',
            'v4',
            'entries',
            path_params={
                'queue': QUEUE[self.queue]['name'],
                'tier': TIER[self.tier],
                'division': DIVISION[self.division]
            },
            query_params={'page': page_num}
        )

        if page_result['status'] == 'OK':
            result = len(page_result['data'])

        return result

    def page_write(self, max_page: int):
        """
        Записывает максимальную страницу в хранилище
        :param max_page: Максимальная страница
        """
        record_to_find = {
            'platform': self.platform,
            'queue': self.queue,
            'tier': self.tier,
            'division': self.division
        }
        record_to_update = {
            'max_page': max_page
        }

        return self._update('page_list', record_to_find, record_to_update)

    def get_random_summoner_list(self) -> List:
        """
        Генерирует рандомную страницу призывателей
        :return: Список идетификаторов призывателей
        """
        summoner_list = []

        # для низкого эло
        if self.tier < 10:
            max_page = self.get_max_page().get('max_page', 0)

            if max_page == 0:
                max_page = 10

            summoner_page = random.randint(1, max_page)

            page_result = self.get_request(
                self.platform,
                'league',
                'v4',
                'entries',
                path_params={
                    'queue': QUEUE[self.queue]['name'],
                    'tier': TIER[self.tier],
                    'division': DIVISION[self.division]
                },
                query_params={'page': summoner_page}
            )

            if page_result.get('status') == 'OK':
                summoner_list = page_result.get('data')
        # для высокого эло
        else:
            # генерируем страницу призывателей для высокого ело
            high_elo_result = self.get_request(
                self.platform,
                'league',
                'v4',
                LEAGUE[self.tier] + '/by-queue',
                path_params={
                    'queue': QUEUE[self.queue]['name']
                }
            )

            if high_elo_result.get('status') == 'OK':
                summoner_list = high_elo_result.get('data').get('entries')

        return summoner_list
