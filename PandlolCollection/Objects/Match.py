from datetime import datetime
from pymongo import MongoClient
from typing import Dict

from PandlolCollection.Objects.LOLObject import LOLObject
from PandlolCollection.Objects.MatchDetail import MatchDetail
from PandlolCollection.Objects.MatchTimeline import MatchTimeline


class Match(LOLObject):
    """
    Объект матча
    """
    def __init__(
            self,
            connection: MongoClient,
            record: Dict):
        self.__match_detail = MatchDetail(
            connection=connection,
            record={
                "platform": record.get("platform"),
                "id": record.get("id")
            }
        )
        self.__match_timeline = MatchTimeline(
            connection=connection,
            record={
                "platform": record.get("platform"),
                "id": record.get("id")
            }
        )
        super().__init__(
            connection=connection,
            record=record,
            table_name='match_list',
            find_field=['id', 'platform'],
            update_field=['date_insert', 'date_update']
        )

    @property
    def platform(self) -> str:
        return self._record.get('platform')

    @property
    def id(self) -> str:
        return self._record.get('id')

    def write(self) -> Dict:
        """
        Метод записывает детали матча в базу
        :return: Количество записанных матчей
        """
        result = {"status": 'OK', 'result': 0}

    #   start = datetime.now()
        # запишем детали матча
        result_match_detail = self.__match_detail.write()
    #    result_match_detail = {"status": 'OK', 'result': 10}
    #    print(f"Match detail has been written in {datetime.now() - start} seconds")

        # если все хорошо, запишем таймлайн матча
        if result_match_detail['status'] == 'OK':
            if result_match_detail['result'] > 0:
                # start = datetime.now()
                result_match_timeline = self.__match_timeline.write()
        #        print(f"Match timeline has been written in {datetime.now() - start} seconds")

                # Если все хорошо, запишем дату обновления матча
                if result_match_timeline['status'] == 'OK':
                    result['result'] += 1
                else:
                    result = result_match_timeline
        else:
            result = result_match_detail

        return result
