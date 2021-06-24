import json

from datetime import datetime
from pymongo import MongoClient
from typing import Dict, List

from PandlolCollection.constant import QUEUE
from PandlolCollection.Objects.LOLObject import LOLObject
from PandlolCollection.Objects.Summoner import Summoner


class MatchDetail(LOLObject):
    """
    Класс деталей матча. Названия свойств = найзваниям полей в таблице
    """
    def __init__(
            self,
            connection: MongoClient,
            record: Dict
    ):
        self.__id = record["id"]
        self.__platform = record["platform"]
        self.__connection = connection

        super().__init__(
            connection=connection,
            record=record,
            table_name='match_detail',
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
    def queue(self) -> int:
        """
        Код очереди
        """
        return self._record['queue']

    @queue.setter
    def queue(self, value: int):
        self._record['queue'] = value

    @property
    def time_create(self) -> datetime:
        """
        Дата и время создания игры
        """
        return self._record['time_create']

    @time_create.setter
    def time_create(self, value: datetime):
        self._record['time_create'] = value

    @property
    def time_start(self) -> datetime:
        """
        Дата и время создания игры
        """
        return self._record['time_start']

    @time_start.setter
    def time_start(self, value: datetime):
        self._record['time_start'] = value

    @property
    def duration(self) -> int:
        """
        Продолжительность игры в секундах
        """
        return self._record['duration']

    @duration.setter
    def duration(self, value: int):
        self._record['duration'] = value

    @property
    def version(self) -> str:
        """
        Полная версия игры
        """
        return self._record['version']

    @version.setter
    def version(self, value: str):
        self._record['version'] = value

    @property
    def patch(self) -> str:
        """
        Патч, на котором была игра
        """
        return self._record['patch']

    @patch.setter
    def patch(self, value: str):
        self._record['patch'] = value

    @property
    def team_code(self) -> int:
        """
        Код команды. Константа TEAM
        """
        return self._record['team_code']

    @team_code.setter
    def team_code(self, value: int):
        self._record['team_code'] = value

    @property
    def puu_id(self) -> str:
        """
        PUUID призывателя
        """
        return self._record['puu_id']

    @puu_id.setter
    def puu_id(self, value: str):
        self._record['puu_id'] = value

    @property
    def summoner_id(self) -> str:
        """
        Идентификатор призывателя
        """
        return self._record['summoner_id']

    @summoner_id.setter
    def summoner_id(self, value: str):
        self._record['summoner_id'] = value

    @property
    def tier(self) -> int:
        """
        Ранг призывателя
        """
        return self._record['tier']

    @tier.setter
    def tier(self, value: int):
        self._record['tier'] = value

    @property
    def division(self) -> int:
        """
        Дивизион призывателя
        """
        return self._record['division']

    @division.setter
    def division(self, value: int):
        self._record['division'] = value

    @property
    def participant_code(self) -> int:
        """
        Код призывателя в игре
        """
        return self._record['participant_code']

    @participant_code.setter
    def participant_code(self, value: int):
        self._record['participant_code'] = value

    @property
    def champion_ban(self) -> str:
        """
        Забаненый чемпион
        """
        return self._record['champion_ban']

    @champion_ban.setter
    def champion_ban(self, value: str):
        self._record['champion_ban'] = value

    @property
    def champion_pick(self) -> str:
        """
        Выбранный чемпиона
        """
        return self._record['champion_pick']

    @champion_pick.setter
    def champion_pick(self, value: str):
        self._record['champion_pick'] = value

    @property
    def position_team(self) -> str:
        """
        Позиция в команде
        """
        return self._record['position_team']

    @position_team.setter
    def position_team(self, value: str):
        self._record['position_team'] = value

    @property
    def position_individual(self) -> str:
        """
        Индивидуальная позиция
        """
        return self._record['position_individual']

    @position_individual.setter
    def position_individual(self, value: str):
        self._record['position_individual'] = value

    @property
    def lane(self) -> str:
        """
        Линия
        """
        return self._record['lane']

    @lane.setter
    def lane(self, value: str):
        self._record['lane'] = value

    @property
    def role(self) -> str:
        """
        Роль
        """
        return self._record['role']

    @role.setter
    def role(self, value: str):
        self._record['role'] = value

    @property
    def rune(self) -> Dict:
        """
        Информация о рунах
        """
        return self._record['rune']

    @rune.setter
    def rune(self, value: Dict):
        self._record['rune'] = value

    @property
    def kda(self) -> Dict:
        """
        КДА
        """
        return self._record['kda']

    @kda.setter
    def kda(self, value: Dict):
        self._record['kda'] = value

    @property
    def multikill(self) -> Dict:
        """
        Множественные убийства
        """
        return self._record['multikill']

    @multikill.setter
    def multikill(self, value: Dict):
        self._record['multikill'] = value

    @property
    def first(self) -> Dict:
        """
        Первые
        """
        return self._record['first']

    @first.setter
    def first(self, value: Dict):
        self._record['first'] = value

    @property
    def damage_deal(self) -> Dict:
        """
        Нанесено урона
        """
        return self._record['damage_deal']

    @damage_deal.setter
    def damage_deal(self, value: Dict):
        self._record['damage_deal'] = value

    @property
    def damage_take(self) -> Dict:
        """
        Получено урона
        """
        return self._record['damage_take']

    @damage_take.setter
    def damage_take(self, value: Dict):
        self._record['damage_take'] = value

    @property
    def defense(self) -> Dict:
        return self._record['defense']

    @defense.setter
    def defense(self, value: Dict):
        self._record['defense'] = value

    @property
    def gold(self) -> Dict:
        return self._record['gold']

    @gold.setter
    def gold(self, value: Dict):
        self._record['gold'] = value

    @property
    def vision(self) -> Dict:
        return self._record['vision']

    @vision.setter
    def vision(self, value: Dict):
        self._record['vision'] = value

    @property
    def object(self) -> Dict:
        return self._record['object']

    @object.setter
    def object(self, value: Dict):
        self._record['object'] = value

    @property
    def other(self) -> Dict:
        return self._record['other']

    @other.setter
    def other(self, value: Dict):
        self._record['other'] = value

    @property
    def champion_exp(self) -> int:
        return self._record['champion_exp']

    @champion_exp.setter
    def champion_exp(self, value: int):
        self._record['champion_exp'] = value

    @property
    def champion_level(self) -> int:
        return self._record['champion_level']

    @champion_level.setter
    def champion_level(self, value: int):
        self._record['champion_level'] = value

    @property
    def mantra1_id(self) -> int:
        return self._record['mantra1_id']

    @mantra1_id.setter
    def mantra1_id(self, value: int):
        self._record['mantra1_id'] = value

    @property
    def mantra1_count(self) -> int:
        return self._record['mantra1_count']

    @mantra1_count.setter
    def mantra1_count(self, value: int):
        self._record['mantra1_count'] = value

    @property
    def mantra2_id(self) -> int:
        return self._record['mantra2_id']

    @mantra2_id.setter
    def mantra2_id(self, value: int):
        self._record['mantra2_id'] = value

    @property
    def mantra2_count(self) -> int:
        return self._record['mantra2_count']

    @mantra2_count.setter
    def mantra2_count(self, value: int):
        self._record['mantra2_count'] = value

    @property
    def spell1_count(self) -> int:
        return self._record['spell1_count']

    @spell1_count.setter
    def spell1_count(self, value: int):
        self._record['spell1_count'] = value

    @property
    def spell2_count(self) -> int:
        return self._record['spell2_count']

    @spell2_count.setter
    def spell2_count(self, value: int):
        self._record['spell2_count'] = value

    @property
    def spell3_count(self) -> int:
        return self._record['spell3_count']

    @spell3_count.setter
    def spell3_count(self, value: int):
        self._record['spell3_count'] = value

    @property
    def spell4_count(self) -> int:
        return self._record['spell4_count']

    @spell4_count.setter
    def spell4_count(self, value: int):
        self._record['spell4_count'] = value

    @property
    def item_list(self) -> List:
        return self._record['item_list']

    @item_list.setter
    def item_list(self, value: List):
        self._record['item_list'] = value

    @property
    def item_count(self) -> int:
        return self._record['item_count']

    @item_count.setter
    def item_count(self, value: int):
        self._record['item_count'] = value

    @property
    def item_consumable(self) -> int:
        return self._record['item_consumable']

    @item_consumable.setter
    def item_consumable(self, value: int):
        self._record['item_consumable'] = value

    @property
    def time_play(self) -> int:
        return self._record['time_play']

    @time_play.setter
    def time_play(self, value: int):
        self._record['time_play'] = value

    @property
    def early_surr(self) -> bool:
        return self._record['early_surr']

    @early_surr.setter
    def early_surr(self, value: bool):
        self._record['early_surr'] = value

    @property
    def surr(self) -> bool:
        return self._record['surr']

    @surr.setter
    def surr(self, value: bool):
        self._record['surr'] = value

    @property
    def win(self) -> bool:
        return self._record['win']

    @win.setter
    def win(self, value: bool):
        self._record['win'] = value

    def write(self) -> Dict:
        """
        Метод записи деталей матча
        :return: Результат
        """
        result = {'status': 'OK', 'result': 0}

        # получим детали матча из API
        result_api = self.get_request(
            platform=self.__platform,
            api='match',
            version='v5',
            api_type='matches',
            path_params={"match_id": self.__id}
        )

        # Обрабатываем API
        if result_api['status'] == 'OK':
            # Загрузим список чемпионов
            f = open('PandlolCollection/champion.json', 'r')

            champion_list = json.loads(f.read())
            champion_list = champion_list['data']

            f.close()

            info = result_api['data'].get('info')
            if info:
                if info.get('queueId', 0) in QUEUE:
                    participant_list = result_api['data']['info'].get('participants')
                    team_list = result_api['data']['info'].get('teams')

                    early_surr = False

                    # уберем игру, если она с ранней сдачей
                    for participant in participant_list:
                        if participant["teamEarlySurrendered"]:
                            early_surr = True

                    if not early_surr:
                        for participant in participant_list:
                            # Обнуляем все поля
                            self._record.clear()

                            # Записываем значения
                            # Общая информация об игре
                            self.match_id = self.__id
                            self.platform = self.__platform
                            self.queue = info.get('queueId', 0)
                            self.time_create = datetime.fromtimestamp(info.get('gameCreation', 0) / 1000)
                            self.time_start = datetime.fromtimestamp(info.get('gameStartTimestamp', 0) / 1000)
                            self.duration = round(info.get('gameDuration', 0) / 1000)
                            self.version = info.get('gameVersion')
                            self.patch = ".".join(self.version.split(sep='.')[0:2])

                            # Информация о призывателе
                            self.team_code = int(participant.get("teamId", "0"))
                            self.puu_id = participant.get("puuid")
                            self.summoner_id = participant.get("summonerId")

                            summoner = Summoner(
                                connection=self.__connection,
                                record={
                                    "platform": self.platform,
                                    "id": self.summoner_id
                                }
                            )
                            summoner.get_by_id()

                            self.tier = 0
                            self.division = 1
                            for rank in summoner.rank:
                                if rank['queue'] == self.queue:
                                    self.tier = rank['tier']
                                    self.division = rank['division']

                            self.participant_code = participant.get("participantId", 0)

                            # бан
                            for team in team_list:
                                if team['teamId'] == self.team_code:
                                    for ban in team['bans']:
                                        if ban['pickTurn'] == self.participant_code:
                                            for key, champion in champion_list.items():
                                                if int(champion['key']) == ban.get('championId', 0):
                                                    self.champion_ban = key

                            # выбранный чемпион
                            self.champion_pick = participant.get('championName')

                            # позиция игрока
                            self.position_team = participant.get('teamPosition')
                            self.position_individual = participant.get('individualPosition')
                            self.lane = participant.get('lane')
                            self.role = participant.get('role')

                            # руны
                            perks = participant['perks']
                            primary = {}
                            sub = {}

                            for style in perks['styles']:
                                if style["description"] == "primaryStyle":
                                    primary = style
                                if style['description'] == "subStyle":
                                    sub = style

                            self.rune = {
                                'defense': perks['statPerks']['defense'],
                                'flex': perks['statPerks']['flex'],
                                'offense': perks['statPerks']['offense'],
                                'primary': {
                                    'branch': primary['style'],
                                    'rune_first': primary['selections'][0]['perk'],
                                    'rune_first_var_list': {
                                        'var1': primary['selections'][0]['var1'],
                                        'var2': primary['selections'][0]['var2'],
                                        'var3': primary['selections'][0]['var3']
                                    },
                                    'rune_second': primary['selections'][1]['perk'],
                                    'rune_second_var_list': {
                                        'var1': primary['selections'][1]['var1'],
                                        'var2': primary['selections'][1]['var2'],
                                        'var3': primary['selections'][1]['var3']
                                    },
                                    'rune_third': primary['selections'][2]['perk'],
                                    'rune_third_var_list': {
                                        'var1': primary['selections'][2]['var1'],
                                        'var2': primary['selections'][2]['var2'],
                                        'var3': primary['selections'][2]['var3']
                                    },
                                    'rune_fourth': primary['selections'][3]['perk'],
                                    'rune_fourth_var_list': {
                                        'var1': primary['selections'][3]['var1'],
                                        'var2': primary['selections'][3]['var2'],
                                        'var3': primary['selections'][3]['var3']
                                    }
                                },
                                'sub': {
                                    'branch': sub['style'],
                                    'rune_first': sub['selections'][0]['perk'],
                                    'rune_first_var_list': {
                                        'var1': sub['selections'][0]['var1'],
                                        'var2': sub['selections'][0]['var2'],
                                        'var3': sub['selections'][0]['var3']
                                    },
                                    'rune_second': sub['selections'][1]['perk'],
                                    'rune_second_var_list': {
                                        'var1': sub['selections'][1]['var1'],
                                        'var2': sub['selections'][1]['var2'],
                                        'var3': sub['selections'][1]['var3']
                                    }
                                }
                            }

                            # КДА
                            self.kda = {
                                'kill_count': participant.get('kills', 0),
                                'death_count': participant.get('deaths', 0),
                                'assist_count': participant.get('assists', 0)
                            }

                            # Множественные убийства
                            self.multikill = {
                                'doublekill_count': participant.get('doubleKills', 0),
                                'triplekill_count': participant.get('tripleKills', 0),
                                'quadrakill_count': participant.get('quadraKills', 0),
                                'pentakill_count': participant.get('pentaKills', 0),
                                'multikill_best': participant.get('largestMultiKill', 0),
                                'killing_spree_count': participant.get('killingSprees', 0),
                                'killing_spree_best': participant.get('largestKillingSpree', 0)
                            }

                            # Первые
                            self.first = {
                                'blood_assist': participant.get('firstBloodAssist', False),
                                'blood_kill': participant.get('firstBloodKill', False),
                                'tower_assist': participant.get('firstTowerAssist', False),
                                'tower_kill': participant.get('firstTowerKill', False)
                            }

                            # Нанесено урона
                            self.damage_deal = {
                                'total': participant.get('totalDamageDealt', 0),
                                'total_champion': participant.get('totalDamageDealtToChampions', 0),
                                'physical': participant.get('physicalDamageDealt', 0),
                                'physical_champion': participant.get('physicalDamageDealtToChampions', 0),
                                'magic': participant.get('magicDamageDealt', 0),
                                'magic_champion': participant.get('magicDamageDealtToChampions', 0),
                                'true': participant.get('trueDamageDealt', 0),
                                'true_champion': participant.get('trueDamageDealtToChampions', 0),
                            }

                            # Получено урона
                            self.damage_take = {
                                'total': participant.get('totalDamageTaken', 0),
                                'physical': participant.get('physicalDamageTaken', 0),
                                'magic': participant.get('magicDamageTaken', 0),
                                'true': participant.get('trueDamageTaken', 0)
                            }

                            # Защита
                            self.defense = {
                                'total_teammate_shield': participant.get('totalDamageShieldedOnTeammates', 0),
                                'multigate_damage': participant.get('damageSelfMitigated', 0),
                                'total_heal': participant.get('totalHeal', 0),
                                'total_heal_teammate': participant.get('totalHealsOnTeammates', 0)
                            }

                            # Золото
                            self.gold = {
                                'earn': participant.get('goldEarned', 0),
                                'spend': participant.get('goldSpent', 0)
                            }

                            # Обзор
                            self.vision = {
                                'detector_ward_place': participant.get('detectorWardsPlaced', 0),
                                'detector_ward_buy': participant.get('visionWardsBoughtInGame', 0),
                                'ward_kill_count': participant.get('wardsKilled', 0),
                                'ward_place_count': participant.get('wardsPlaced', 0),
                                'score': participant.get('visionScore', 0)
                            }

                            # Объекты
                            self.object = {
                                'total_damage': participant.get('damageDealtToObjectives', 0),
                                'building_damage': participant.get('damageDealtToBuildings', 0),
                                'turret_damage': participant.get('damageDealtToTurrets', 0),
                                'minion_kill_count': participant.get('totalMinionsKilled', 0),
                                'monster_kill_count': participant.get('neutralMinionsKilled', 0),
                                'baron_kill_count': participant.get('baronKills', 0),
                                'dragon_kill_count': participant.get('dragonKills', 0),
                                'object_steal_count': participant.get('objectivesStolen', 0),
                                'object_steal_assist': participant.get('objectivesStolenAssists', 0),
                                'turret_kill_count': participant.get('turretKills', 0),
                                'turret_lost_count': participant.get('turretsLost', 0),
                                'inhibitor_kill_count': participant.get('inhibitorKills', 0),
                                'inhibitor_lost_count': participant.get('inhibitorsLost', 0),
                                'nexus_kill_count': participant.get('nexusKills', 0),
                                'nexus_lost_count': participant.get('nexusLost', 0),
                            }

                            # Прочая статистика
                            self.other = {
                                'critical_strike_best': participant.get('largestCriticalStrike', 0),
                                'total_dead_time': participant.get('totalTimeSpentDead', 0),
                                'living_time_best': participant.get('longestTimeSpentLiving', 0)
                            }

                            # Опыт чемпиона
                            self.champion_exp = participant.get('champExperience', 0)

                            # Уровень чемпиона
                            self.champion_level = participant.get('champLevel', 0)

                            # Заклинания призывателя
                            self.mantra1_id = participant.get('summoner1Id', 0)
                            self.mantra1_count = participant.get('summoner1Casts', 0)
                            self.mantra2_id = participant.get('summoner2Id', 0)
                            self.mantra2_count = participant.get('summoner2Casts', 0)

                            # Умения чемпиона
                            self.spell1_count = participant.get('spell1Casts', 0)
                            self.spell2_count = participant.get('spell2Casts', 0)
                            self.spell3_count = participant.get('spell3Casts', 0)
                            self.spell4_count = participant.get('spell4Casts', 0)

                            # Предметы
                            item_list = []
                            if participant.get('item0', 0) != 0:
                                item_list.append(participant.get('item0', 0))
                            if participant.get('item1', 0) != 0:
                                item_list.append(participant.get('item1', 0))
                            if participant.get('item2', 0) != 0:
                                item_list.append(participant.get('item2', 0))
                            if participant.get('item3', 0) != 0:
                                item_list.append(participant.get('item3', 0))
                            if participant.get('item4', 0) != 0:
                                item_list.append(participant.get('item4', 0))
                            if participant.get('item5', 0) != 0:
                                item_list.append(participant.get('item5', 0))
                            if participant.get('item6', 0) != 0:
                                item_list.append(participant.get('item6', 0))
                            self.item_list = item_list.copy()

                            self.item_count = participant.get('itemsPurchased', 0)
                            self.item_consumable = participant.get('consumablesPurchased', 0)

                            # Время в игре
                            self.time_play = participant.get('timePlayed', 0)

                            # Сдача
                            self.early_surr = participant.get('gameEndedInEarlySurrender', False)
                            self.surr = participant.get('gameEndedInSurrender', False)

                            # Победа
                            self.win = participant.get('win', False)

                            # добавим запись в список
                            self.append()

                        result_insert = self.insert_many()

                        if result_insert['status'] == 'OK':
                            result = {'status': 'OK', 'result': len(result_insert['result'].inserted_ids)}
                        else:
                            result = result_insert

        return result
