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
                "id": record.get("match_id")
            }
        )
        self.__match_timeline = MatchTimeline(
            connection=connection,
            record={
                "platform": record.get("platform"),
                "id": record.get("match_id")
            }
        )
        super().__init__(
            connection=connection,
            record=record,
            table_name='match_detail',
            find_field=['match_id', 'platform']
        )

    def write(self) -> Dict:
        """
        Метод записывает детали матча в базу
        :return: Количество записанных матчей
        """
        result = {"status": 'OK', 'result': 0}

        # запишем детали матча
        result_match_detail = self.__match_detail.write()
        # result_match_detail = {'status': 'OK', 'result': 10}

        # если все хорошо, запишем таймлайн матча
        if result_match_detail['status'] == 'OK':
            if result_match_detail['result'] > 0:
                result_match_timeline = self.__match_timeline.write()

                # Если все хорошо, запишем дату обновления матча
                if result_match_timeline['status'] == 'OK':
                    result['result'] += 1
                else:
                    result = result_match_timeline
        else:
            result = result_match_detail

        return result
