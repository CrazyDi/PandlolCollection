from datetime import datetime
from typing import Dict

from PandlolCollection.Objects.LOLObject import LOLObject


class Match(LOLObject):
    """
    Объект матча
    """
    @property
    def platform(self) -> str:
        return self._record.get('platform')

    @property
    def id(self) -> str:
        return self._record.get('id')

    def insert(self) -> Dict:
        """
        Запись матча в хранилище
        :return:
        """
        record_to_find = {'matchId': self.id}
        find_result = self._read_one('match_test', record_to_find)

        if find_result.get('status') == 'OK' and find_result.get('result') is None:
            record_to_insert = {
                'matchId': self.id,
                'platform': self.platform,
                'dateInsert': datetime.today(),
                'dateUpdate': None
            }
            result = self._insert('match_test', record_to_insert)
        else:
            result = find_result

        return result
