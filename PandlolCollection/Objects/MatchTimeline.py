from pymongo import MongoClient
from typing import Dict

from PandlolCollection.Objects.LOLObject import LOLObject


class MatchTimeline:
    """
    Фабрика обработки таймлайна матча
    """
    def __init__(
            self,
            connection: MongoClient,
            record: Dict
    ):
        self.__id = record.get("id")
        self.__platform = record.get("platform")
        self.__match_state = MatchState(
            connection=connection,
            record={
                "platform": self.__platform,
                "id": self.__id
            }
        )

        self.__match_event = MatchEvent(
            connection=connection,
            record={
                "platform": self.__platform,
                "id": self.__id
            }
        )

    def write(self):
        pass


class MatchState(LOLObject):
    """
    Класс статов персонажей в матче
    """
    def __init__(
            self,
            connection: MongoClient,
            record: Dict
    ):
        super().__init__(
            connection=connection,
            record=record,
            table_name='match_state',
            find_field=['platform', 'id'],
            update_field=[]
        )

    @property
    def platform(self) -> str:
        return self._record.get('platform')

    @property
    def id(self) -> str:
        return self._record.get('id')


class MatchEvent(LOLObject):
    """
    Класс событий матча
    """
    def __init__(
            self,
            connection: MongoClient,
            record: Dict
    ):
        super().__init__(
            connection=connection,
            record=record,
            table_name='match_event',
            find_field=['platform', 'id'],
            update_field=[]
        )

    @property
    def platform(self) -> str:
        return self._record.get('platform')

    @property
    def id(self) -> str:
        return self._record.get('id')
