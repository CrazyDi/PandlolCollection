from pymongo import MongoClient
from typing import Dict

from PandlolCollection.Objects.LOLObject import LOLObject
from PandlolCollection.Objects.MatchDetail import MatchDetail
from PandlolCollection.Objects.MatchEvent import BaseEvent


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

        self.__base_event = BaseEvent(connection=connection)

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
                match_detail_list = []
                # прочитаем информацию о деталях матча
                result_match_detail = self.__match_detail.read_many()
                if result_match_detail['status'] == 'OK':
                    match_detail_list = list(result_match_detail['result'])

                # заполним информацию об участниках матча
                participant_list = {
                    participant['participant_code']: {
                        "match_id": participant['match_id'],
                        "queue": participant['queue'],
                        "platform": participant['platform'],
                        "patch": participant['patch'],
                        "tier": participant['tier'],
                        "division": participant['division'],
                        "puu_id": participant['puu_id'],
                        "champion_name": participant['champion_pick'],
                        "team_code": participant["team_code"],
                        "surr": participant["surr"],
                        "early_surr": participant["early_surr"]
                    } for participant in match_detail_list
                }

                # По каждой записи в таймлайне
                for frame in info.get("frames"):
                    # запишем события
                    self.__base_event.write(frame.get("events"), participant_list)

                    # if result_match_event['status'] == 'OK':
                    #     result['result'] += result_match_event['result']

                    # запишем статы
                    result_match_state = self.__match_state.write(
                        frame.get("participantFrames"),
                        frame.get("timestamp"),
                        participant_list
                    )

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

    def write(self, state_list: Dict, timestamp: int, participant_list: Dict) -> Dict:
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
