import random

from datetime import datetime

from PandlolCollection.RIOTConnector import RIOTConnector
from PandlolCollection.MongoDBConnector import MongoDBConnector
from PandlolCollection.Summoner import Summoner
from PandlolCollection.constant import TIER, DIVISION, QUEUE, PLATFORM, LEAGUE


class Loader:
    def __init__(self):
        self.tier = -1
        self.division = -1
        self.queue = 420
        self.platform = ''
        self.db_connector = None

    def load_random_data(self):
        """
        Загрузка случайных игр 11 сезона
        """
        self.db_connector = MongoDBConnector()

        # По каждой платформе
        for platform in PLATFORM:
            self.platform = platform
            # По каждому рангу
            for tier in TIER:
                self.tier = tier

                # Для низкого эло
                if tier < 10:
                    division_list = DIVISION
                else: # для высого это рангов нет, возьмем только один
                    division_list = {1: "I"}

                # По каждому дивизиону
                for division in division_list:
                    start = datetime.now()

                    self.division = division

                    result = self.load_random_match_list(count_summoner=10)

                    end = datetime.now()

                    print(
                        'PLATFORM:', platform,
                        '\nTIER: ', TIER[tier],
                        '\nDIVISION:', DIVISION[division],
                        '\nRESULT:', result,
                        '\nSTART:', start.strftime("%b %d %H:%M:%S"),
                        '\nEND:', end.strftime("%b %d %H:%M:%S"),
                        '\nTIME:', (end - start).seconds
                    )

        # Закрываем соединение
        self.db_connector.close_connection()

    def load_random_match_list(self, count_summoner: int = 100):
        """
        Загрузка заданного количества рандомных матчей по параметрам
        :param count_summoner: Кол-во призывателей, матчи которых надо загрузить
        :return: Кол-во загруженных матчей
        """
        i = 1
        result = 0

        # Выбрать заданное количество призывателей
        while i < count_summoner:
            # Выберем список матчей рандомного призывателя
            match_list = self.load_match_list_random_summoner()

            for match_id in match_list:
                count_matches = self.write_random_match(match_id)
                result += count_matches

            i += 1

        return result

    def write_random_match(self, match_id):
        """
        Запись найденного матча в файл
        :param match_id: Идентификатор мачта
        :return: Кол-во записанных матчей
        """
        result = 0

        record_to_find = {'matchId': match_id}

        find_result = self.db_connector.read_record('match_list', record_to_find)

        if find_result.get('status') == 'OK':
            if find_result.get('result') is None:
                record_to_insert = {'matchId': match_id,
                                    'platform': self.platform,
                                    'dateInsert': datetime.today(),
                                    'dateUpdate': None}
                insert_result = self.db_connector.insert_record('match_list', record_to_insert)

                if insert_result['status'] == 'OK':
                    result = 1

        return result

    def load_match_list_random_summoner(self, count_matches=100):
        """
        Функция ищет указанное количество матчей рандомного призывателя
        :param count_matches: Кол-во матчей
        :return: Кол-во матчей
        """

        match_list = []

        # для начала найдем рандомного призывателя
        result = self.load_random_summoner()
        if result.get('status') == 'OK':
            summoner_id = result.get('summonerId')

            # найдем его puuid
            summoner = self.get_summoner_by_id(summoner_id)
            if summoner:
                # сгенерируем рандомную страницу
                max_page = int((datetime.today().isocalendar()[1] * 10) / count_matches)
                page = random.randint(0, max_page - 1)

                while (len(match_list) == 0) & (max_page > 0):
                    match_list = summoner.get_summoner_match_list(start=page * count_matches, count=count_matches)
                    max_page = int(max_page / 2)

        return match_list

    def load_random_summoner(self):
        max_page = 100
        summoner_list = []

        # генерируем рандомную страницу призывателей для низкого эло
        if self.tier < 10:
            while len(summoner_list) == 0:
                if max_page < 1:
                    max_page = 1

                summoner_page = random.randint(1, max_page)

                page_result = self.load_random_summoner_page(summoner_page)
                if page_result.get('status') == 'OK':
                    summoner_list = page_result.get('data')

                max_page = int(max_page / 2)
        else:
            high_elo_connector = RIOTConnector(self.platform, 'league', 'v4', LEAGUE[self.tier] + '/by-queue',
                                               path_params={'queue': QUEUE[self.queue]['name']})
            result = high_elo_connector.get_request()
            if result.get('status') == 'OK':
                summoner_list = high_elo_connector.get_request().get('data').get('entries')

        if len(summoner_list) > 0:
            # выбираем рандомного призывателя
            summoner_num = random.randint(0, len(summoner_list)-1)
            result = {'status': 'OK',
                      'summonerId': summoner_list[summoner_num].get('summonerId')}
        else:
            result = {'status': 'error'}

        return result

    def load_random_summoner_page(self, summoner_page):
        """
        Выбор рандомной страницы призывателей низкого эло
        :param summoner_page: Номер рандомной страницы
        :return: Результат запроса
        """
        low_elo_connector = RIOTConnector(self.platform, 'league', 'v4', 'entries',
                                       path_params={
                                           'queue': QUEUE[self.queue]['name'],
                                           'tier': TIER[self.tier],
                                           'division': DIVISION[self.division]
                                       },
                                       query_params={'page': summoner_page})
        return low_elo_connector.get_request()

    def get_summoner_by_id(self, summoner_id):
        riot_connector = RIOTConnector(self.platform, 'summoner', 'v4', 'summoners',
                                           path_params={'summonerId': summoner_id})
        response = riot_connector.get_request()

        summoner = None
        if response['status'] == 'OK':
            summoner = Summoner(platform=self.platform,
                                summoner_id=summoner_id,
                                account_id=response['data']['accountId'],
                                puuid=response['data']['puuid'],
                                summoner_name=response['data']['name'])

        return summoner
