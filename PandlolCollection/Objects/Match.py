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

    def write(self):
        """
        Метод записывает детали матча в базу
        :return: Количество записанных матчей
        """
        result = 0

        # запишем детали матча
        result_match_detail = self.__match_detail.write()

        # если все хорошо, запишем таймлайн матча
        if result_match_detail['status'] == 'OK':
            # if result_match_detail['result'] > 0:
            # result_match_timeline = self.__match_timeline.write()

            # Если все хорошо, запишем дату обновления матча
            # if result_match_timeline['status'] == 'OK':
            result_update = self.update()
            if result_update['status'] == 'OK':
                result = result_update['result'].modified_count

        return result
