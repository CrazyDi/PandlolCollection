from datetime import datetime
from pymongo import MongoClient
from typing import Dict, List

from PandlolCollection.building import BUILDING_LIST
from PandlolCollection.Objects.LOLObject import LOLObject
from PandlolCollection.Objects.MatchDetail import MatchDetail


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

        self.__match_detail = MatchDetail(
            connection=connection,
            record={
                "platform": self.__platform,
                "id": self.__id,
                "match_id": self.__id
            }
        )

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

    def write(self) -> Dict:
        """
        Метод записи таймлайна матча
        :return:
        """
        result = {'status': 'OK', 'result': 0}

        # Возьмем данные из API
        result_api = LOLObject.get_request(
            platform=self.__platform,
            api='match',
            version='v5',
            api_type='matches',
            path_params={"match_id": self.__id},
            type_params='timeline'
        )

        # Обрабатываем API
        if result_api['status'] == 'OK':
            info = result_api['data'].get('info')

            if info:
                # прочитаем информацию о деталях матча
                result_match_detail = self.__match_detail.read_many()
                if result_match_detail['status'] == 'OK':
                    match_detail_list = list(result_match_detail['result'])

                    # заполним информацию об участниках матча
                    participant_list = {
                        participant['participant_code']: {
                            "puu_id": participant['puu_id'],
                            "champion_name": participant['champion_pick'],
                            "team_code": participant["team_code"]
                        } for participant in match_detail_list
                    }
                    print("match_timeline")
                    # По каждой записи в таймлайне
                    for frame in info.get("frames"):
                        # запишем события
                        result_match_event = self.__match_event.write(frame.get("events"), participant_list)

                        if result_match_event['status'] == 'OK':
                            result['result'] += result_match_event['result']

                        # запишем статы
                        result_match_state = self.__match_state.write(
                            frame.get("participantFrames"),
                            participant_list,
                            frame.get("timestamp"))

                        if result_match_state['status'] == 'OK':
                            result['result'] += result_match_state['result']

        return result


class MatchState(LOLObject):
    """
    Класс статов персонажей в матче
    """
    def __init__(
            self,
            connection: MongoClient,
            record: Dict
    ):
        self.__id = record['id']
        self.__platform = record['platform']
        super().__init__(
            connection=connection,
            record=record,
            table_name='match_state',
            find_field=['platform', 'match_id'],
            update_field=[]
        )

    @property
    def match_id(self) -> str:
        """
        Идентификатор матча
        """
        return self._record.get("match_id")

    @match_id.setter
    def match_id(self, value: str):
        self._record['match_id'] = value

    @property
    def platform(self) -> str:
        """
        Платформа
        """
        return self._record["platform"]

    @platform.setter
    def platform(self, value: str):
        self._record['platform'] = value

    @property
    def participant_code(self) -> int:
        return self._record["participant_code"]

    @participant_code.setter
    def participant_code(self, value: int):
        self._record["participant_code"] = value

    @property
    def puu_id(self) -> str:
        return self._record["puu_id"]

    @puu_id.setter
    def puu_id(self, value: str):
        self._record["puu_id"] = value

    @property
    def champion_name(self) -> str:
        return self._record["champion_name"]

    @champion_name.setter
    def champion_name(self, value: str):
        self._record["champion_name"] = value

    @property
    def timestamp(self) -> int:
        return self._record["timestamp"]

    @timestamp.setter
    def timestamp(self, value: int):
        self._record["timestamp"] = value

    @property
    def champion_level(self) -> int:
        return self._record["champion_level"]

    @champion_level.setter
    def champion_level(self, value: int):
        self._record["champion_level"] = value

    @property
    def champion_experience(self) -> int:
        return self._record["champion_experience"]

    @champion_experience.setter
    def champion_experience(self, value: int):
        self._record["champion_experience"] = value

    @property
    def state(self) -> Dict:
        return self._record["state"]

    @state.setter
    def state(self, value: Dict):
        self._record["state"] = value

    @property
    def damage_deal(self) -> Dict:
        return self._record["damage_deal"]

    @damage_deal.setter
    def damage_deal(self, value: Dict):
        self._record["damage_deal"] = value

    @property
    def damage_take(self) -> Dict:
        return self._record["damage_take"]

    @damage_take.setter
    def damage_take(self, value: Dict):
        self._record["damage_take"] = value

    @property
    def gold(self) -> Dict:
        return self._record["gold"]

    @gold.setter
    def gold(self, value: Dict):
        self._record["gold"] = value

    @property
    def minion(self) -> Dict:
        return self._record["minion"]

    @minion.setter
    def minion(self, value: Dict):
        self._record["minion"] = value

    @property
    def control_time(self) -> int:
        return self._record["control_time"]

    @control_time.setter
    def control_time(self, value: int):
        self._record["control_time"] = value

    @property
    def position(self) -> Dict:
        return self._record["position"]

    @position.setter
    def position(self, value: Dict):
        self._record["position"] = value

    def write(self, state_list: Dict, participant_list: Dict, timestamp: int) -> Dict:
        """
        Метод записи статов участника
        :param state_list: Статы из API
        :param participant_list: Список участников матча
        :param timestamp: Время записи стата
        :return: Результат записи
        """
        self._record_list.clear()
        for code, participant in participant_list.items():
            # Обнуляем все поля
            self._record.clear()

            participant_code = str(code)

            # Информация о матче
            self.match_id = self.__id
            self.platform = self.__platform

            # Информация об участнике
            self.participant_code = code
            self.puu_id = participant.get("puu_id")
            self.champion_name = participant.get("champion_name")

            # Время
            self.timestamp = round(timestamp / 1000)

            # Уровень чемпиона
            self.champion_level = state_list[participant_code].get("level", 0)
            self.champion_experience = state_list[participant_code].get("xp", 0)

            # Показатели чемпиона
            self.state = {
                "ability_power": state_list[participant_code]["championStats"].get("abilityPower", 0),
                "armor": state_list[participant_code]["championStats"].get("armor", 0),
                "armor_pen": state_list[participant_code]["championStats"].get("armorPen", 0),
                "armor_pen_percent": state_list[participant_code]["championStats"].get("armorPenPercent", 0),
                "attack_damage": state_list[participant_code]["championStats"].get("attackDamage", 0),
                "attack_speed": state_list[participant_code]["championStats"].get("attackSpeed", 0),
                "bonus_armor": state_list[participant_code]["championStats"].get("bonusArmorPenPercent", 0),
                "bonus_magic": state_list[participant_code]["championStats"].get("bonusMagicPenPercent", 0),
                "cool_down_reduction": state_list[participant_code]["championStats"].get("ccReduction", 0),
                "health": state_list[participant_code]["championStats"].get("health", 0),
                "health_max": state_list[participant_code]["championStats"].get("healthMax", 0),
                "health_regen": state_list[participant_code]["championStats"].get("healthRegen", 0),
                "life_steal": state_list[participant_code]["championStats"].get("lifesteal", 0),
                "magic_pen": state_list[participant_code]["championStats"].get("magicPen", 0),
                "magic_pen_percent": state_list[participant_code]["championStats"].get("magicPenPercent", 0),
                "magic_resist": state_list[participant_code]["championStats"].get("magicResist", 0),
                "movement_speed": state_list[participant_code]["championStats"].get("movementSpeed", 0),
                "power": state_list[participant_code]["championStats"].get("power", 0),
                "power_max": state_list[participant_code]["championStats"].get("powerMax", 0),
                "power_regen": state_list[participant_code]["championStats"].get("powerRegen", 0),
                "spell_vamp": state_list[participant_code]["championStats"].get("spellVamp", 0),
            }

            # Нанесенный урон
            self.damage_deal = {
                "magic": state_list[participant_code]["damageStats"].get("magicDamageDone", 0),
                "magic_champion": state_list[participant_code]["damageStats"].get("magicDamageDoneToChampions", 0),
                "physical": state_list[participant_code]["damageStats"].get("physicalDamageDone", 0),
                "physical_champion": state_list[participant_code]["damageStats"].get("physicalDamageDoneToChampions", 0),
                "true": state_list[participant_code]["damageStats"].get("trueDamageDone", 0),
                "true_champion": state_list[participant_code]["damageStats"].get("trueDamageDoneToChampions", 0),
                "total": state_list[participant_code]["damageStats"].get("totalDamageDone", 0),
                "total_champion": state_list[participant_code]["damageStats"].get("totalDamageDoneToChampions", 0),
            }

            # Полученный урон
            self.damage_take = {
                "magic": state_list[participant_code]["damageStats"].get("magicDamageTaken", 0),
                "physical": state_list[participant_code]["damageStats"].get("physicalDamageTaken", 0),
                "true": state_list[participant_code]["damageStats"].get("true", 0),
                "total": state_list[participant_code]["damageStats"].get("totalDamageTaken", 0)
            }

            # Золото
            self.gold = {
                "current": state_list[participant_code].get("currentGold", 0),
                "total": state_list[participant_code].get("totalGold", 0),
                "per_second": state_list[participant_code].get("goldPerSecond", 0)
            }

            # Информация о миньонах
            self.minion = {
                "jungle_kill_count": state_list[participant_code].get("jungleMinionsKilled", 0),
                "kill_count": state_list[participant_code].get("minionsKilled", 0),
            }

            # Время, проведенное в контроле
            self.control_time = round(state_list[participant_code].get("timeEnemySpentControlled", 0) / 1000)

            # Позиция
            self.position = {
                "x": state_list[participant_code]["position"].get("x", 0),
                "y": state_list[participant_code]["position"].get("y", 0),
            }

            # добавим запись в список
            self.append()

        result_insert = self.insert_many()

        if result_insert['status'] == 'OK':
            result = {
                'status': 'OK',
                'result': len(result_insert['result'].inserted_ids)
            }
        else:
            result = result_insert

        return result


class MatchEvent(LOLObject):
    """
    Класс событий матча
    """
    __participant_list = {}

    def __init__(
            self,
            connection: MongoClient,
            record: Dict
    ):
        self.__id = record["id"]
        self.__platform = record["platform"]
        super().__init__(
            connection=connection,
            record=record,
            table_name='match_event',
            find_field=['platform', 'match_id'],
            update_field=[]
        )

    @property
    def match_id(self) -> str:
        return self._record.get("match_id")

    @match_id.setter
    def match_id(self, value: str):
        self._record['match_id'] = value

    @property
    def platform(self) -> str:
        return self._record["platform"]

    @platform.setter
    def platform(self, value: str):
        self._record['platform'] = value

    @property
    def timestamp(self) -> int:
        return self._record["timestamp"]

    @timestamp.setter
    def timestamp(self, value: int):
        self._record["timestamp"] = value

    @property
    def event_type(self) -> str:
        return self._record["event_type"]

    @event_type.setter
    def event_type(self, value: str):
        self._record["event_type"] = value

    @property
    def team_code(self) -> int:
        return self._record["team_code"]

    @team_code.setter
    def team_code(self, value: int):
        self._record["team_code"] = value

    @property
    def participant_code(self) -> int:
        return self._record["participant_code"]

    @participant_code.setter
    def participant_code(self, value: int):
        self._record["participant_code"] = value

    @property
    def puu_id(self) -> str:
        return self._record["puu_id"]

    @puu_id.setter
    def puu_id(self, value: str):
        self._record["puu_id"] = value

    @property
    def champion_name(self) -> str:
        return self._record["champion_name"]

    @champion_name.setter
    def champion_name(self, value: str):
        self._record["champion_name"] = value

    @property
    def event(self) -> Dict:
        return self._record["event"]

    @event.setter
    def event(self, value: Dict):
        self._record["event"] = value

    def __write_base(
            self,
            timestamp: int,
            event_type: str,
            participant_code: int = 0,
            team_code: int = None
    ) -> int:
        """
        Функция записи базовых параметров события
        :param timestamp: Время события
        :param event_type: Тип события
        :param participant_code: Код участника матча
        :param team_code: Код команды, если нет конкретного участника
        :return Количество заполненных полей
        """
        self._record.clear()

        self.match_id = self.__id
        self.platform = self.__platform
        self.timestamp = round(timestamp / 1000)
        self.event_type = event_type

        # Если указан участник матча, записываем участника
        if participant_code > 0:
            self.participant_code = participant_code
            self.team_code = self.__participant_list[participant_code]["team_code"]
            self.puu_id = self.__participant_list[participant_code]["puu_id"]
            self.champion_name = self.__participant_list[participant_code]["champion_name"]
        else:
            # Если не указан участник, но указана команда
            if team_code:
                self.team_code = team_code

        return len(self._record)

    def __write_match_begin_end(self, event: Dict):
        self.event = {"real_timestamp": datetime.fromtimestamp(event.get("realTimestamp", 0) / 1000)}

        self.append()

        return len(self.event)

    def __write_skill_level_up(self, event: Dict):
        self.event = {"skill_code": event.get("skillSlot", 0)}

        self.append()

        return len(self.event)

    def __write_level_up(self, event: Dict):
        self.event = {"level": event.get("level", 0)}

        self.append()

        return len(self.event)

    def __write_item(self, event: Dict):
        self.event = {"item_id": event.get("itemId", 0)}

        self.append()

        return len(self.event)

    def __write_ward(self, event: Dict):
        self.event = {"ward_type": event.get("wardType")}

        self.append()

        return len(self.event)

    def __write_building(self, event: Dict):
        self.event = {
            "lane": "UNKNOWN",
            "building_type": "UNKNOWN",
            "turret_type": "UNKNOWN"
        }

        for building in BUILDING_LIST:
            if building["position"] == event.get("position", {}):
                self.event = {
                    "lane": building["lane"],
                    "building_type": building["building_type"],
                    "turret_type": building["turret_type"]
                }

        self.append()

        return len(self.event)

    def __write_monster(self, event: Dict):
        self.event = {
            "monster_type": event.get("monsterType"),
            "monster_sub_type": event.get("monsterSubType"),
            "position": event.get("position", None)
        }

        self.append()

        return len(self.event)

    def __write_soul(self, event: Dict):
        self.event = {
            "soul_type": event.get("name")
        }

        self.append()

        return len(self.event)

    def __write_kill(self, event: Dict, special_event_list: List):

        self.event = {
            "victim_id": event.get("victimId"),
            "gold_bounty": event.get("bounty", 0),
            "kill_streak": event.get("killStreakLength", 0),
            "position": event.get("position", None)
        }

        for kill in special_event_list:
            if kill["timestamp"] == event["timestamp"] and kill["killerId"] == event["killerId"]:
                if kill["killType"] == "KILL_FIRST_BLOOD":
                    self.event["first_blood"] = 1
                if kill["killType"] == "KILL_MULTI":
                    self.event["multikill"] = kill["multiKillLength"]
                if kill["killType"] == "KILL_ACE":
                    self.event["ace"] = 1

        self.append()

        return len(self.event)

    def __write_death(self, event: Dict):
        self.event = {
            "killer_id": event.get("killerId", 0),
            "position": event.get("position", None)
        }

        self.append()

        return len(self.event)

    def __write_assist(self, event: Dict):
        self.event = {
            "victim_id": event.get("victimId", 0),
            "position": event.get("position", None)
        }

        self.append()

        return len(self.event)

    def __write_unknown_event(self, event: str):
        with open("unknown.event", "a") as f:
            f.write(event + ', ' + str(self.__id) + '\n')

    def write(self, event_list: List, participant_list: Dict) -> Dict:
        """
        Запись событий игры
        :param event_list: Список событий
        :param participant_list: Список участников
        :return: Результат
        """
        self.__participant_list = participant_list
        self._record_list.clear()

        # выберем отдельно пометки убийств и удалим их из основного списка
        special_kill_list = []
        for event in event_list:
            if event["type"] == "CHAMPION_SPECIAL_KILL":
                special_kill_list.append(event)

        # обработаем каждое события
        for event in event_list:
            # Начало игры
            if event["type"] == "PAUSE_END":
                self.__write_base(event.get("timestamp", 0), "MATCH_BEGIN")
                self.__write_match_begin_end(event)

            # Поднятие уровня чемпиона
            elif event["type"] == "LEVEL_UP":
                self.__write_base(event.get("timestamp", 0), "SKILL_LEVEL_UP",
                                  participant_code=event.get("participantId", 0))
                self.__write_level_up(event)

            # Поднятие уровня заклинания
            elif event["type"] == "SKILL_LEVEL_UP":
                self.__write_base(event.get("timestamp", 0), "SKILL_LEVEL_UP",
                                  participant_code=event.get("participantId", 0))
                self.__write_skill_level_up(event)

            # Покупка предмета, уничтожение предмета
            elif event["type"] in ["ITEM_PURCHASED", "ITEM_DESTROYED", "ITEM_UNDO", "ITEM_SOLD"]:
                self.__write_base(event.get("timestamp", 0), event["type"],
                                  participant_code=event.get("participantId", 0))
                self.__write_item(event)

            # Установка варда
            elif event["type"] == "WARD_PLACED":
                self.__write_base(event.get("timestamp", 0), event["type"],
                                  participant_code=event.get("creatorId", 0))
                self.__write_ward(event)

            # Убийство варда
            elif event["type"] == "WARD_KILL":
                self.__write_base(event.get("timestamp", 0), event["type"],
                                  participant_code=event.get("killerId", 0))
                self.__write_ward(event)

            # Уничтожение строения или пластины
            elif event["type"] in ["TURRET_PLATE_DESTROYED", "BUILDING_KILL"]:
                if event.get("teamId", 0) == 100:
                    team_code = 200
                elif event.get("teamId", 0) == 200:
                    team_code = 100
                else:
                    team_code = None

                self.__write_base(event.get("timestamp", 0), event["type"],
                                  participant_code=event.get("killerId", 0),
                                  team_code=team_code)
                self.__write_building(event)

                for participant in event.get("assistingParticipantIds", []):
                    event_type = "BUILDING_ASSIST"
                    if event["type"] == "TURRET_PLATE_DESTROYED":
                        event_type = "TURRET_PLATE_ASSIST"

                    self.__write_base(event.get("timestamp", 0), event_type,
                                      participant_code=participant)
                    self.__write_building(event)

            # Убийство элитного монстра
            elif event["type"] == "ELITE_MONSTER_KILL":
                if event.get("killerId", 0) == 0:
                    team_code = event.get("killerTeamId", 0)
                else:
                    team_code = None
                self.__write_base(event.get("timestamp", 0), event["type"],
                                  participant_code=event.get("killerId", 0),
                                  team_code=team_code)
                self.__write_monster(event)

                for participant in event.get("assistingParticipantIds", []):
                    event_type = "ELITE_MONSTER_ASSIST"

                    self.__write_base(event.get("timestamp", 0), event_type,
                                      participant_code=participant)
                    self.__write_monster(event)

            # Получение души дракона
            elif event["type"] == "DRAGON_SOUL_GIVEN":
                self.__write_base(event.get("timestamp", 0), event["type"],
                                  team_code=event.get("teamId"))
                self.__write_soul(event)

            # Убийство чемпиона
            elif event["type"] == "CHAMPION_KILL":
                # если убийство совершил чемпион
                if event.get("killerId", 0) > 0:
                    # запишем убийство
                    self.__write_base(event.get("timestamp", 0), event["type"],
                                      participant_code=event.get("killerId", 0))
                    self.__write_kill(event, special_kill_list)

                    # запишем смерть
                    self.__write_base(event.get("timestamp", 0), "CHAMPION_DEATH",
                                      participant_code=event.get("victimId", 0))
                    self.__write_death(event)

                    # запишем содействия
                    for participant in event.get("assistingParticipantIds", []):
                        self.__write_base(event.get("timestamp", 0), "CHAMPION_ASSIST",
                                          participant_code=participant)
                        self.__write_assist(event)

            # Окончание игры
            elif event["type"] == "GAME_END":
                self.__write_base(event.get("timestamp", 0), "MATCH_END", team_code=event.get("winningTeam", 0))
                self.__write_match_begin_end(event)
            # пропускаем отдельные события
            elif event["type"] in ["CHAMPION_SPECIAL_KILL", "CHAMPION_TRANSFORM"]:
                pass
            else:
                self.__write_unknown_event(event["type"])

        result_insert = self.insert_many()

        if result_insert['status'] == 'OK':
            if result_insert['result']:
                result = {
                    'status': 'OK',
                    'result': len(result_insert['result'].inserted_ids)
                }
            else:
                result = {
                    'status': 'OK',
                    'result': 0
                }
        else:
            result = result_insert

        return result
