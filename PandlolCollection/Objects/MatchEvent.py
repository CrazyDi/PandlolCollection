from datetime import datetime
from pymongo import MongoClient
from typing import Dict, List

from PandlolCollection.Objects.LOLObject import LOLObject
from PandlolCollection.building import BUILDING_LIST


class BaseEvent:
    """
    Фабрика событий матча
    """
    def __init__(self, connection: MongoClient):
        self.connection = connection

    @staticmethod
    def base_record(
            participant_list: Dict,
            timestamp: int,
            event_type: str,
            participant_code: int = 0,
            team_code: int = None
    ) -> Dict:
        """
        Функция записи базовых параметров события
        :param participant_list: Список участников матча
        :param timestamp: Время события
        :param event_type: Тип события
        :param participant_code: Код участника матча
        :param team_code: Код команды, если нет конкретного участника
        :return Количество заполненных полей
        """
        if participant_code > 0:
            record = {
                "match_id": participant_list[participant_code]["match_id"],
                "patch": participant_list[participant_code]["patch"],
                "queue": participant_list[participant_code]["queue"],
                "platform": participant_list[participant_code]["platform"],
                "team_code": participant_list[participant_code]["team_code"],
                "participant_code": participant_code,
                "puu_id": participant_list[participant_code]["puu_id"],
                "champion_name": participant_list[participant_code]["champion_name"],
                "event_type": event_type,
                "timestamp": round(timestamp / 1000)
            }
        else:
            record = {
                "match_id": participant_list[1]["match_id"],
                "patch": participant_list[1]["patch"],
                "queue": participant_list[1]["queue"],
                "platform": participant_list[1]["platform"],
                "team_code": team_code,
                "event_type": event_type,
                "timestamp": round(timestamp / 1000)
            }

        return record

    def write(self, event_list: List, participant_list: Dict):
        # выберем отдельно пометки убийств
        special_kill_list = []
        for event in event_list:
            if event["type"] == "CHAMPION_SPECIAL_KILL":
                special_kill_list.append(event)

        for event in event_list:
            # Начало и окончание игры
            if event["type"] in ["PAUSE_END", "GAME_END"]:
                record = {
                    "match_id": participant_list[1]["match_id"],
                    "patch": participant_list[1]["patch"],
                    "queue": participant_list[1]["queue"],
                    "platform": participant_list[1]["platform"]
                }
                new_event = EventBeginEnd(connection=self.connection, record=record)
                new_event.write(event, participant_list)

            elif event["type"] == "LEVEL_UP":
                record = self.base_record(
                    participant_list,
                    event["timestamp"],
                    event_type=event["type"],
                    participant_code=event.get("participantId", 0)
                )
                new_event = EventLevel(connection=self.connection, record=record)
                new_event.write(event)

            elif event["type"] == "SKILL_LEVEL_UP":
                record = self.base_record(
                    participant_list,
                    event["timestamp"],
                    event_type=event["type"],
                    participant_code=event.get("participantId", 0)
                )
                new_event = EventSkill(connection=self.connection, record=record)
                new_event.write(event)

            elif event["type"] in ["ITEM_PURCHASED", "ITEM_DESTROYED", "ITEM_UNDO", "ITEM_SOLD"]:
                record = self.base_record(
                    participant_list,
                    event["timestamp"],
                    event_type=event["type"],
                    participant_code=event.get("participantId", 0)
                )
                new_event = EventItem(connection=self.connection, record=record)
                new_event.write(event)

            elif event["type"] == "WARD_PLACED":
                record = self.base_record(
                    participant_list,
                    event["timestamp"],
                    event_type=event["type"],
                    participant_code=event.get("creatorId", 0)
                )
                new_event = EventWard(connection=self.connection, record=record)
                new_event.write(event)

            elif event["type"] == "WARD_KILL":
                record = self.base_record(
                    participant_list,
                    event["timestamp"],
                    event_type=event["type"],
                    participant_code=event.get("killerId", 0)
                )
                new_event = EventWard(connection=self.connection, record=record)
                new_event.write(event)

            elif event["type"] in ["TURRET_PLATE_DESTROYED", "BUILDING_KILL"]:
                if event.get("teamId", 0) == 100:
                    team_code = 200
                elif event.get("teamId", 0) == 200:
                    team_code = 100
                else:
                    team_code = None

                record = self.base_record(
                    participant_list,
                    event["timestamp"],
                    event_type=event["type"],
                    participant_code=event.get("killerId", 0),
                    team_code=team_code
                )
                new_event = EventBuilding(connection=self.connection, record=record)
                new_event.write(event)

                for participant in event.get("assistingParticipantIds", []):
                    event_type = "BUILDING_ASSIST"
                    if event["type"] == "TURRET_PLATE_DESTROYED":
                        event_type = "TURRET_PLATE_ASSIST"

                    record = self.base_record(
                        participant_list,
                        event["timestamp"],
                        event_type=event_type,
                        participant_code=participant,
                        team_code=team_code
                    )
                    new_event = EventBuilding(connection=self.connection, record=record)
                    new_event.write(event)

            elif event["type"] == "ELITE_MONSTER_KILL":
                if event.get("killerId", 0) == 0:
                    team_code = event.get("killerTeamId", 0)
                else:
                    team_code = None

                record = self.base_record(
                    participant_list,
                    event["timestamp"],
                    event_type=event["type"],
                    participant_code=event.get("killerId", 0),
                    team_code=team_code
                )
                new_event = EventMonster(connection=self.connection, record=record)
                new_event.write(event)

                for participant in event.get("assistingParticipantIds", []):
                    event_type = "ELITE_MONSTER_ASSIST"

                    record = self.base_record(
                        participant_list,
                        event["timestamp"],
                        event_type=event_type,
                        participant_code=participant
                    )
                    new_event = EventMonster(connection=self.connection, record=record)
                    new_event.write(event)

            elif event["type"] == "DRAGON_SOUL_GIVEN":
                record = self.base_record(
                    participant_list,
                    event["timestamp"],
                    event_type=event["type"],
                    team_code=event.get("teamId")
                )
                new_event = EventDragonSoul(connection=self.connection, record=record)
                new_event.write(event)

            elif event["type"] == "CHAMPION_KILL":
                if event.get("killerId", 0) > 0:
                    # запишем убийство
                    record = self.base_record(
                        participant_list,
                        event["timestamp"],
                        event_type=event["type"],
                        participant_code=event.get("killerId", 0)
                    )
                    kill_event = EventChampion(connection=self.connection, record=record)
                    kill_event.write_kill(event, special_kill_list)

                    # запишем смерть
                    record = self.base_record(
                        participant_list,
                        event["timestamp"],
                        event_type="CHAMPION_DEATH",
                        participant_code=event.get("victimId", 0)
                    )
                    kill_event = EventChampion(connection=self.connection, record=record)
                    kill_event.write_death(event)

                    # запишем содействия
                    for participant in event.get("assistingParticipantIds", []):
                        record = self.base_record(
                            participant_list,
                            event["timestamp"],
                            event_type="CHAMPION_ASSIST",
                            participant_code=participant
                        )
                        assist_event = EventChampion(connection=self.connection, record=record)
                        assist_event.write_assist(event)


class EventBeginEnd(LOLObject):
    """
    Событие начала - окончания матча
    """
    def __init__(self,
                 connection: MongoClient,
                 record: Dict
                 ):
        super().__init__(
            connection=connection,
            record=record,
            table_name="event_begin_end",
            find_field=['match_id'],
            update_field=['end_time', 'duration', 'team_win', 'surr', 'early_surr']
        )

    @property
    def begin_time(self):
        return self._record["begin_time"]

    @begin_time.setter
    def begin_time(self, value):
        self._record["begin_time"] = value

    @property
    def end_time(self):
        return self._record["end_time"]

    @end_time.setter
    def end_time(self, value):
        self._record["end_time"] = value

    @property
    def duration(self) -> int:
        return self._record["duration"]

    @duration.setter
    def duration(self, value: int):
        self._record["duration"] = value

    @property
    def team_win(self) -> int:
        return self._record["team_win"]

    @team_win.setter
    def team_win(self, value: int):
        self._record["team_win"] = value

    @property
    def surr(self) -> bool:
        return self._record["surr"]

    @surr.setter
    def surr(self, value: bool):
        self._record["surr"] = value

    @property
    def early_surr(self) -> bool:
        return self._record["early_surr"]

    @early_surr.setter
    def early_surr(self, value: bool):
        self._record["early_surr"] = value

    def write(self, event: Dict, participant_list: Dict):
        if event["type"] == "PAUSE_END":
            self.begin_time = datetime.fromtimestamp(event.get("realTimestamp", 0) / 1000)
            self.insert()

        if event["type"] == "GAME_END":
            self.end_time = datetime.fromtimestamp(event.get("realTimestamp", 0) / 1000)
            self.duration = round(event["timestamp"] / 1000)
            self.team_win = event.get("winningTeam", 0)

            self.surr = False
            self.early_surr = False

            for participant_code in range(1, 10):
                if participant_list[participant_code]["surr"] and not self.surr:
                    self.surr = True

                if participant_list[participant_code]["early_surr"] and not self.early_surr:
                    self.early_surr = True

            self.update()


class EventLevel(LOLObject):
    """
    Прокачка уровня чемпиона
    """
    def __init__(self,
                 connection: MongoClient,
                 record: Dict
                 ):
        super().__init__(
            connection=connection,
            record=record,
            table_name="event_level"
        )

    @property
    def level(self) -> int:
        return self._record["level"]

    @level.setter
    def level(self, value: int):
        self._record["level"] = value

    def write(self, event):
        self.level = event.get("level", 0)
        self.insert()


class EventSkill(LOLObject):
    """
    Прокачка скиллов
    """
    def __init__(self,
                 connection: MongoClient,
                 record: Dict
                 ):
        super().__init__(
            connection=connection,
            record=record,
            table_name="event_skill"
        )

    @property
    def skill_code(self) -> int:
        return self._record["skill_code"]

    @skill_code.setter
    def skill_code(self, value: int):
        self._record["skill_code"] = value

    def write(self, event):
        self.skill_code = event.get("skillSlot", 0)
        self.insert()


class EventItem(LOLObject):
    """
    Действие с предметом
    """
    def __init__(self,
                 connection: MongoClient,
                 record: Dict
                 ):
        super().__init__(
            connection=connection,
            record=record,
            table_name="event_item"
        )

    @property
    def item_id(self) -> int:
        return self._record["item_id"]

    @item_id.setter
    def item_id(self, value: int):
        self._record["item_id"] = value

    def write(self, event):
        if event["type"] == "ITEM_UNDO":
            self.item_id = event.get("beforeId", 0)
        else:
            self.item_id = event.get("itemId", 0)
        self.insert()


class EventWard(LOLObject):
    """
    Установка или уничтожение варда
    """
    def __init__(self,
                 connection: MongoClient,
                 record: Dict
                 ):
        super().__init__(
            connection=connection,
            record=record,
            table_name="event_ward"
        )

    @property
    def ward_type(self) -> str:
        return self._record["ward_type"]

    @ward_type.setter
    def ward_type(self, value: str):
        self._record["ward_type"] = value

    def write(self, event):
        self.ward_type = event.get("wardType")
        self.insert()


class EventBuilding(LOLObject):
    """
    Разрушение объекта
    """
    def __init__(
            self,
            connection: MongoClient,
            record: Dict
    ):
        super().__init__(
            connection=connection,
            record=record,
            table_name="event_building"
        )

    @property
    def lane(self) -> str:
        return self._record["lane"]

    @lane.setter
    def lane(self, value: str):
        self._record["lane"] = value

    @property
    def building_type(self) -> str:
        return self._record["building_type"]

    @building_type.setter
    def building_type(self, value: str):
        self._record["building_type"] = value

    @property
    def turret_type(self) -> str:
        return self._record["turret_type"]

    @turret_type.setter
    def turret_type(self, value: str):
        self._record["turret_type"] = value

    def write(self, event):
        for building in BUILDING_LIST:
            if building["position"] == event.get("position", {}):
                self.lane = building["lane"]
                self.building_type = building["building_type"]
                self.turret_type = building["turret_type"]

        self.insert()


class EventMonster(LOLObject):
    """
    Убийство монстра
    """
    def __init__(self,
                 connection: MongoClient,
                 record: Dict
                 ):
        super().__init__(
            connection=connection,
            record=record,
            table_name="event_monster"
        )

    @property
    def monster_type(self) -> str:
        return self._record["monster_type"]

    @monster_type.setter
    def monster_type(self, value: str):
        self._record["monster_type"] = value

    @property
    def monster_sub_type(self) -> str:
        return self._record["monster_sub_type"]

    @monster_sub_type.setter
    def monster_sub_type(self, value: str):
        self._record["monster_sub_type"] = value

    @property
    def position(self):
        return self._record["position"]

    @position.setter
    def position(self, value: str):
        self._record["position"] = value

    def write(self, event):
        self.monster_type = event.get("monsterType")
        self.monster_sub_type = event.get("monsterSubType")
        self.position = event.get("position", None)
        self.insert()


class EventDragonSoul(LOLObject):
    """
    Получение души дракона
    """
    def __init__(self,
                 connection: MongoClient,
                 record: Dict
                 ):
        super().__init__(
            connection=connection,
            record=record,
            table_name="event_dragon_soul",
            find_field=["match_id"]
        )

    @property
    def soul_type(self) -> str:
        return self._record["soul_type"]

    @soul_type.setter
    def soul_type(self, value: str):
        self._record["soul_type"] = value

    def write(self, event):
        self.soul_type = event.get("name")
        res = self.read_one()
        if res["status"] == 'OK':
            if res['result'] is None:
                self.insert()


class EventChampion(LOLObject):
    """
    Убийство чемпиона
    """
    def __init__(self,
                 connection: MongoClient,
                 record: Dict
                 ):
        super().__init__(
            connection=connection,
            record=record,
            table_name="event_champion"
        )

    @property
    def participant_event(self) -> int:
        return self._record["participant_event"]

    @participant_event.setter
    def participant_event(self, value: int):
        self._record["participant_event"] = value

    @property
    def gold_bounty(self) -> int:
        return self._record["gold_bounty"]

    @gold_bounty.setter
    def gold_bounty(self, value: int):
        self._record["gold_bounty"] = value

    @property
    def kill_streak(self) -> int:
        return self._record["kill_streak"]

    @kill_streak.setter
    def kill_streak(self, value: int):
        self._record["kill_streak"] = value

    @property
    def position(self):
        return self._record["position"]

    @position.setter
    def position(self, value):
        self._record["position"] = value

    @property
    def first_blood(self) -> bool:
        return self._record["first_blood"]

    @first_blood.setter
    def first_blood(self, value: bool):
        self._record["first_blood"] = value

    @property
    def ace(self) -> bool:
        return self._record["ace"]

    @ace.setter
    def ace(self, value: bool):
        self._record["ace"] = value

    @property
    def multikill(self) -> int:
        return self._record["multikill"]

    @multikill.setter
    def multikill(self, value: int):
        self._record["multikill"] = value

    def write_kill(self, event, special_event_list):
        self.participant_event = event.get("victimId")
        self.gold_bounty = event.get("bounty", 0)
        self.kill_streak = event.get("killStreakLength", 0)
        self.position = event.get("position", None)

        for kill in special_event_list:
            if kill["timestamp"] == event["timestamp"] and kill["killerId"] == event["killerId"]:
                if kill["killType"] == "KILL_FIRST_BLOOD":
                    self.first_blood = True
                if kill["killType"] == "KILL_MULTI":
                    self.multikill = kill["multiKillLength"]
                if kill["killType"] == "KILL_ACE":
                    self.ace = True
        self.insert()

    def write_death(self, event):
        self.participant_event = event.get("killerId", 0)
        self.position = event.get("position", None)
        self.insert()

    def write_assist(self, event):
        self.participant_event = event.get("victimId", 0)
        self.position = event.get("position", None)
        self.insert()
