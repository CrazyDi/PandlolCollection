from PandlolCollection.RIOTConnector import RIOTConnector


class Summoner:
    """
    Класс получение информации по призывателю
    """
    def __init__(self, platform, summoner_id, account_id, puuid, summoner_name):
        self.platform = platform
        self.id = summoner_id
        self.account_id = account_id
        self.puuid = puuid
        self.summoner_name = summoner_name

    def get_summoner_match_list(self, start=0, count=20):
        riot_connector = RIOTConnector(self.platform, 'match', 'v5', 'matches/by-puuid',
                                       path_params={'puuid': self.puuid},
                                       type_params='ids',
                                       query_params={'start': start,
                                                     'count': count})
        response = riot_connector.get_request()
        if response['status'] == 'OK':
            result = response['data']
        else:
            result = []

        return result
