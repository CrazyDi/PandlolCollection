from pymongo import MongoClient
from typing import Dict

from PandlolCollection.Objects.LOLObject import LOLObject
from PandlolCollection.Objects.MatchDetail import MatchDetail


class Match(LOLObject):
    """
    Объект матча
    """
    def __init__(
            self,
            connection: MongoClient,
            record: Dict):
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

    @property
    def match_detail(self) -> MatchDetail:
        return self._record.get('match_detail')
