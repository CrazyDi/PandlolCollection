from PandlolCollection.RIOTConnector import RIOTConnector
from PandlolCollection.MongoDBConnector import MongoDBConnector
from PandlolCollection.constant import TIER, DIVISION, QUEUE, PLATFORM


class Loader:
    @staticmethod
    def load_summoner_list():
        # коннект к базе
        db_connector = MongoDBConnector()

        # сначала загружаем обычные ранги
        api = 'league'
        api_type = 'entries'

        # по каждому рангу
        for tier in TIER:

            # по каждому дивизиону
            for division in DIVISION:
                # по каждому виду очереди
                for queue in QUEUE:
                    # по каждой платформе
                    for platform in PLATFORM:
                        page = 1
                        # запрашиваем первую страницу
                        api_connector = RIOTConnector(platform, api, api_type,
                                                      path_params={"queue": QUEUE[queue]['name'],
                                                                   "tier": TIER[tier],
                                                                   "division": DIVISION[division]},
                                                      query_params={"page": page})
                        response = api_connector.get_request()

                        # пока есть данные
                        while len(response['data']) > 0:
                            result = response['status']
                            # если все хорошо - записываем данные в базу
                            if response['status'] == "OK":
                                result = db_connector.write_data('summoner_list',
                                                                 response['data'],
                                                                 default_fields={"platform": platform},
                                                                 filter_columns=['summonerId', 'queueType'],
                                                                 value_columns=['summonerName', 'tier', 'rank'])

                            page = page + 1

                            # следующая страница
                            api_connector = RIOTConnector(platform, api, api_type,
                                                          path_params={"queue": QUEUE[queue]['name'],
                                                                       "tier": TIER[tier],
                                                                       "division": DIVISION[division]},
                                                          query_params={"page": page})
                            response = api_connector.get_request()
                            print(result)
                            print(len(response['data']))
                            print(page)

        # загружаем мастеров, грандмастеров, чаликов
        high_elo = {"MASTER": "masterleagues/by-queue",
                    "GRANDMASTER": "grandmasterleagues/by-queue",
                    "CHALLENGER": "challengerleagues/by-queue"}

        # по каждому виду эло
        for elo in high_elo:
            api_type = high_elo[elo]
            # по каждому виду очереди
            for queue in QUEUE:
                # по каждой платформе
                for platform in PLATFORM:
                    # запрашиваем данные
                    api_connector = RIOTConnector(platform, api, api_type,
                                                  path_params={"queue": QUEUE[queue]['name']})
                    response = api_connector.get_request()

                    # записываем данные в таблицу
                    result = response['status']
                    if response['status'] == "OK":
                        result = db_connector.write_data('summoner_list',
                                                         response['data']['entries'],
                                                         default_fields={"platform": platform,
                                                                         "tier": elo,
                                                                         "rank": "I",
                                                                         "queueType": QUEUE[queue]['name']},
                                                         filter_columns=['summonerId'],
                                                         value_columns=['summonerName'])

                    print(result)

        db_connector.close_connection()
        return None
