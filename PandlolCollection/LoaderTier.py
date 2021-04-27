import random

from datetime import datetime

from PandlolCollection.LOLObject import LOLObject
from PandlolCollection.constant import TIER, DIVISION, QUEUE, LEAGUE


class LoaderTier(LOLObject):
    @property
    def platform(self):
        return self._record.get('platform')

    @property
    def queue(self):
        return self._record.get('queue', 420)

    @property
    def tier(self):
        return self._record.get('tier', 1)

    @property
    def division(self):
        return self._record.get('division', 1)

    def load_random_match_list(self, count_summoner: int = 10, count_match: int = 100):
        """
        Загрузка заданного количества рандомных матчей по параметрам
        :param count_summoner: Кол-во призывателей, матчи которых надо загрузить
        :param count_match: Кол-во матчей каждого призывателя, которые надо загрузить
        :return: Кол-во загруженных матчей
        """
        start = datetime.now()

        i = 1
        result = 0
        match_list = []

        # Выбрать заданное количество призывателей
        while i < count_summoner:
            # Выберем список матчей рандомного призывателя
            # для начала найдем рандомного призывателя
            max_page = 100
            summoner_list = []

            # генерируем рандомную страницу призывателей для низкого эло
            if self.tier < 10:
                while len(summoner_list) == 0:
                    if max_page < 1:
                        max_page = 1

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

                    max_page = int(max_page / 2)
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

            if len(summoner_list) > 0:
                # выбираем рандомного призывателя
                summoner_num = random.randint(0, len(summoner_list)-1)
                summoner_result = {
                    'status': 'OK',
                    'summonerId': summoner_list[summoner_num].get('summonerId')
                }
            else:
                summoner_result = {'status': 'error'}

            if summoner_result.get('status') == 'OK':
                summoner_id = summoner_result.get('summonerId')

                # найдем его puuid
                summoner = self.get_request(
                    self.platform,
                    'summoner',
                    'v4',
                    'summoners',
                    path_params={'summonerId': summoner_id}
                )

                if summoner.get('status') == 'OK':
                    puuid = summoner.get('data').get('puuid')
                    max_page = int((datetime.today().isocalendar()[1] * 10) / count_match)

                    match_list = []

                    while (len(match_list) == 0) & (max_page > 0):
                        page = random.randint(0, max_page - 1)
                        result_match = self.get_request(
                            self.platform,
                            'match',
                            'v5',
                            'matches/by-puuid',
                            path_params={'puuid': puuid},
                            type_params='ids',
                            query_params={
                                'start': page * count_match,
                                'count': count_match
                            }
                        )

                        if result_match.get('status') == 'OK':
                            match_list = result_match['data']

                        max_page = int(max_page / 2)

            # По каждому матчу
            for match_id in match_list:
                # Запишем матч в БД
                record_to_find = {'matchId': match_id}
                find_result = self.nosql_read_one('match_test', record_to_find)

                if find_result.get('status') == 'OK' and find_result.get('result') is None:
                    record_to_insert = {
                        'matchId': match_id,
                        'platform': self.platform,
                        'dateInsert': datetime.today(),
                        'dateUpdate': None
                    }
                    insert_result = self.nosql_insert('match_test', record_to_insert)

                    if insert_result['status'] == 'OK':
                        result += 1

            i += 1

        end = datetime.now()

        print(
            'PLATFORM:', self.platform,
            '\nTIER: ', TIER[self.tier],
            '\nDIVISION:', DIVISION[self.division],
            '\nRESULT:', result,
            '\nSTART:', start.strftime("%b %d %H:%M:%S"),
            '\nEND:', end.strftime("%b %d %H:%M:%S"),
            '\nTIME:', (end - start).seconds
        )

        return result

    def load_max_tier_page(self):
            pass