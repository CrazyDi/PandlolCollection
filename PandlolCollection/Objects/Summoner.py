import random

from datetime import datetime
from pymongo import MongoClient
from typing import List, Dict

from PandlolCollection.constant import QUEUE, TIER, DIVISION
from PandlolCollection.Objects.LOLObject import LOLObject


class Summoner(LOLObject):
    """
    Класс призывателя
    """
    def __init__(
            self,
            connection: MongoClient,
            record: Dict):
        super().__init__(
            connection=connection,
            record=record,
            table_name='summoner_list',
            find_field=['platform', 'id'],
            update_field=['account_id', 'puu_id', 'name', 'profile_icon_id', 'date_change', 'rank']
        )

    @property
    def platform(self) -> str:
        return self._record.get('platform')

    @property
    def id(self) -> str:
        return self._record.get('id')

    @property
    def account_id(self) -> str:
        return self._record.get('account_id')

    @property
    def puu_id(self) -> str:
        return self._record.get('puu_id')

    @property
    def name(self) -> str:
        return self._record.get('name')

    @property
    def profile_icon_id(self) -> int:
        return self._record.get('profile_icon_id', 0)

    @property
    def date_change(self) -> datetime:
        return self._record.get('date_change', datetime.today())

    @property
    def rank(self) -> List:
        return self._record.get('rank', [])

    def storage_get_by_id(self) -> Dict:
        """
        Поиск по summoner_id в хранилище
        :return: Результат поиска
        """
        result = {}

        find_result = self.read_one()

        if find_result['status'] == 'OK':
            result = find_result['result']

        return result

    def riot_get_by_id(self) -> Dict:
        """
        Поиск в API по summoner_id
        :return: Результат поиска
        """
        result = {}

        # Находим информацию по призывателю
        summoner_result = self.get_request(
            self.platform,
            'summoner',
            'v4',
            'summoners',
            path_params={'summonerId': self.id}
        )

        if summoner_result['status'] == 'OK':
            # записываем результат
            result['puu_id'] = summoner_result['data']['puuid']
            result['account_id'] = summoner_result['data']['accountId']
            result['name'] = summoner_result['data']['name']
            result['profile_icon_id'] = summoner_result['data']['profileIconId']

            # находим информацию о ранге
            result['rank'] = self.riot_get_rank()

        return result

    def riot_get_rank(self) -> List:
        """
        Получение информации о ранге призывателя
        :return: Список рангов
        """
        result = []

        # найдем информацию о рангах
        rank_result = self.get_request(
            self.platform,
            'league',
            'v4',
            'entries/by-summoner',
            path_params={'summonerId': self.id}
        )

        if rank_result['status'] == 'OK':
            for rank in rank_result['data']:
                row = {}

                # очередь
                for q in QUEUE:
                    if QUEUE[q]['name'] == rank['queueType']:
                        row['queue'] = q

                # тьер
                if row.get('queue'):
                    for t in TIER:
                        if TIER[t] == rank['tier']:
                            row['tier'] = t

                    # дивизион
                    if row.get('tier'):
                        for d in DIVISION:
                            if DIVISION[d] == rank['rank']:
                                row['division'] = d

                if row:
                    row['date_change'] = datetime.today()
                    result.append(row)

        return result

    def get_by_id(self) -> bool:
        """
        Получение полной информации о призывателе по id
        :return: Результат
        """
        result = self.storage_get_by_id()
        if not result:
            result = self.riot_get_by_id()

            # Если запись найдена
            if result:
                # Записываем данные
                self._record['account_id'] = result['account_id']
                self._record['puu_id'] = result['puu_id']
                self._record['name'] = result['name']
                self._record['profile_icon_id'] = result['profile_icon_id']
                self._record['date_change'] = datetime.today()
                self._record['rank'] = result['rank']

            # запишем информацию в хранилище
            self.insert()

        return self.puu_id is not None

    def get_random_match_list(self, count_match) -> List:
        """
        Поиск случайных матчей
        :param count_match: кол-во случайных матчей
        :return: Список матчей
        """
        match_list = []

        # проверяем, заполнен ли puu_id
        if not self.puu_id:
            # достанем из хранилища puu_id
            if self.id:
                if self.get_by_id():
                    # Найдем список матчей
                    max_page = int((datetime.today().isocalendar()[1] * 10) / count_match)

                    while (len(match_list) == 0) & (max_page > 0):
                        page = random.randint(0, max_page - 1)

                        result_match = self.get_request(
                            self.platform,
                            'match',
                            'v5',
                            'matches/by-puuid',
                            path_params={'puuid': self.puu_id},
                            type_params='ids',
                            query_params={
                                'start': page * count_match,
                                'count': count_match
                            }
                        )

                        if result_match.get('status') == 'OK':
                            match_list = result_match['data']

                        max_page = int(max_page / 2)

        return match_list
