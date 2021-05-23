import random

from datetime import datetime, timedelta
from pymongo import MongoClient

from config import Config
from PandlolCollection.constant import PLATFORM, TIER, DIVISION
from PandlolCollection.Objects.Match import Match
from PandlolCollection.Objects.Rank import Rank
from PandlolCollection.Objects.Summoner import Summoner


def load_max_tier_pages():
    """
    Процедура заргузки максимальных страниц призывателей
    """
    # открываем соединение
    connection = MongoClient(Config.NOSQL_CONNECTION_STRING)

    platform_list = PLATFORM
    tier_list = TIER
    division_list = DIVISION

    for platform in platform_list:
        for tier in tier_list:
            # Для низкого эло
            if 10 > tier > 0:
                for division in division_list:
                    start = datetime.now()

                    rank = Rank(
                        connection=connection,
                        record={
                            "platform": platform,
                            "queue": 420,
                            "tier": tier,
                            "division": division
                        }
                    )

                    # найдем текущую максимальную страницу из хранилища
                    max_page = rank.get_max_page()

                    delta = max_page['delta']
                    num = max_page['max_page']

                    curr_page = {
                        'num': num,
                        'len': 0
                    }

                    next_page = {
                        'num': num + 1,
                        'len': 0
                    }

                    not_found = True

                    # пока не найдем последнюю сраницу
                    while not_found:
                        # длина текущей страницы
                        page_len = rank.riot_get_page_len(curr_page['num'])
                        curr_page['len'] = page_len

                        # если текущая страница заполнена
                        if curr_page['len'] > 0:
                            # длина следующей страницы
                            page_len = rank.riot_get_page_len(next_page['num'])
                            next_page['len'] = page_len

                            # если следующая страница пустая
                            if next_page['len'] == 0:
                                # нашли
                                not_found = False
                            else:
                                # увеличиваем диапазон поиска
                                curr_page['num'] += delta
                        # если текущая страница пустая
                        else:
                            # уменьшаем диапазон поиска
                            curr_page['num'] -= delta
                            if curr_page['num'] < 1:
                                curr_page['num'] = 1
                            delta = round(delta / 2)
                            if delta == 0:
                                delta = 1

                        next_page['num'] = curr_page['num'] + 1

                    rank.page_write(curr_page['num'])

                    end = datetime.now()

                    print(
                        'PLATFORM:', platform,
                        '\nTIER: ', TIER[tier],
                        '\nDIVISION:', DIVISION[division],
                        '\nRESULT:', curr_page['num'],
                        '\nSTART:', start.strftime("%b %d %H:%M:%S"),
                        '\nEND:', end.strftime("%b %d %H:%M:%S"),
                        '\nTIME:', (end - start).seconds
                    )

    # закрываем соединение
    connection.close()


def load_random_match_list(count_summoner: int = 10, count_match: int = 100):
    """
    Процедура заргузки случайного списка матчей
    """
    # открываем соединение
    connection = MongoClient(Config.NOSQL_CONNECTION_STRING)

    platform_list = PLATFORM
    tier_list = TIER

    for platform in platform_list:
        for tier in tier_list:
            # Для низкого эло
            if tier < 10:
                division_list = DIVISION
            else:  # для высого это рангов нет, возьмем только один
                division_list = {1: "I"}

            if tier > 0:
                for division in division_list:
                    start = datetime.now()

                    i = 1
                    result = 0

                    # Выбрать заданное количество призывателей
                    while i < count_summoner:
                        # Выберем список матчей рандомного призывателя
                        # для начала найдем рандомного призывателя
                        # генерируем рандомную страницу призывателей для низкого эло
                        rank = Rank(
                            connection=connection,
                            record={
                                "platform": platform,
                                "queue": 420,
                                "tier": tier,
                                "division": division
                            }
                        )
                        summoner_list = rank.get_random_summoner_list()

                        if len(summoner_list) > 0:
                            # выбираем рандомного призывателя
                            summoner_id = summoner_list[random.randint(0, len(summoner_list) - 1)]['summonerId']

                            summoner = Summoner(
                                connection=connection,
                                record={
                                    "platform": platform,
                                    "id": summoner_id
                                }
                            )

                            # Получаем случайный список матчей призывателя
                            match_list = summoner.get_random_match_list(count_match)

                            # По каждому матчу
                            for match_id in match_list:

                                # Запишем матч в БД
                                match = Match(
                                    connection=connection,
                                    record={"platform": platform,
                                            "id": match_id,
                                            "date_insert": datetime.today(),
                                            "date_update": None}
                                )
                                find_result = match.read_one()
                                if find_result['status'] == 'OK' and find_result['result'] is None:
                                    insert_result = match.insert()

                                    if insert_result['status'] == 'OK' and insert_result['result']:
                                        result += 1

                        i += 1

                    end = datetime.now()

                    print(
                        'PLATFORM:', platform,
                        '\nTIER: ', TIER[tier],
                        '\nDIVISION:', DIVISION[division],
                        '\nRESULT:', result,
                        '\nSTART:', start.strftime("%b %d %H:%M:%S"),
                        '\nEND:', end.strftime("%b %d %H:%M:%S"),
                        '\nTIME:', (end - start).seconds
                    )

    # закрываем соединение
    connection.close()


def load_match_details(item_id: str = "", hour: int = 1):
    # открываем соединение
    connection = MongoClient(Config.NOSQL_CONNECTION_STRING)

    start = datetime.now()

    result = 0
    end_time = datetime.now() + timedelta(hours=hour)

    while datetime.now() < end_time:
        if item_id:
            match_item = {
                'id': item_id,
                'platform': item_id.split('_')[0],
                'date_insert': datetime.today()
            }
            end_time = datetime.now()
        else:
            # Найдем рандомный незаполненный матч
            cursor_match = connection.pandlol.match_list.find({"date_update": None})
            list_match = list(cursor_match)

            match_item = random.choice(list_match)

        match_id = match_item['id']
        platform = match_item['platform']

        print(match_id)
        match = Match(
            connection=connection,
            record={"platform": platform,
                    "id": match_id,
                    "date_insert": match_item['date_insert'],
                    "date_update": datetime.today()}
        )
        match_result = match.write()
        if match_result['status'] == 'OK':
            result += match_result['result']

    end = datetime.now()

    print(f'Loaded {result} matches for {(end - start).seconds} seconds at {end.strftime("%b %d %H:%M:%S")}')

    # закрываем соединение
    connection.close()


def load_summoner_list(platform_param: str = "", tier_param: int = 0, division_param: int = 0, count_pages: int = 10000):
    """
    Загрузка призывателей
    """
    # открываем соединение
    connection = MongoClient(Config.NOSQL_CONNECTION_STRING)

    if platform_param:
        platform_list = [platform_param]
    else:
        platform_list = PLATFORM

    if tier_param > 0:
        tier_list = [tier_param]
    else:
        tier_list = TIER

    for platform in platform_list:
        for tier in tier_list:
            # Исключаем UNRANKED
            if tier > 0:
                if tier > 9:
                    division_list = [1]
                else:
                    if division_param > 0:
                        division_list = [division_param]
                    else:
                        division_list = DIVISION

                for division in division_list:
                    start = datetime.now()

                    rank = Rank(
                        connection=connection,
                        record={
                            "platform": platform,
                            "queue": 420,
                            "tier": tier,
                            "division": division
                        }
                    )

                    # Получаем всех призывателей
                    summoner_list = rank.get_rank_summoner_list(count_pages=count_pages)

                    result = 0

                    print(f"Running {platform} {TIER[tier]} {DIVISION[division]}. Total {len(summoner_list)}.")

                    # Загружаем всех призывателей
                    for summoner_item in summoner_list:
                        summoner = Summoner(
                            connection=connection,
                            record={
                                "platform": platform,
                                "id": summoner_item["summonerId"]
                            }
                        )
                        summoner.get_by_id()
                        result += 1
                        with open("summoner_list.log", "a") as f:
                            f.write(f"\n{platform} {TIER[tier]} {DIVISION[division]}. Loaded {result} from {len(summoner_list)}")

                    end = datetime.now()

                    with open("summoner_list.log", "a") as f:
                        f.write(
                            '\nPLATFORM:' + platform +
                            '\nTIER: ' + TIER[tier] +
                            '\nDIVISION:' + DIVISION[division] +
                            '\nRESULT:' + str(result) +
                            '\nSTART:' + start.strftime("%b %d %H:%M:%S") +
                            '\nEND:' + end.strftime("%b %d %H:%M:%S") +
                            '\nTIME:' + str((end - start).seconds))

                    print(
                        'PLATFORM:', platform,
                        '\nTIER: ', TIER[tier],
                        '\nDIVISION:', DIVISION[division],
                        '\nRESULT:', result,
                        '\nSTART:', start.strftime("%b %d %H:%M:%S"),
                        '\nEND:', end.strftime("%b %d %H:%M:%S"),
                        '\nTIME:', (end - start).seconds
                    )


if __name__ == '__main__':
    operation = input("Choose operation:"
                      "\n1: Load max tier pages"
                      "\n2: Load random match list"
                      "\n3: Load match details "
                      "\n4: Load summoner list \n")

    if operation == "1":
        load_max_tier_pages()
    elif operation == "2":
        load_random_match_list()
    elif operation == "3":
        load_match_operation = input("Choose mode:"
                                     "\n1: Load one match by match_id"
                                     "\n2: Load many matches for hours")
        if load_match_operation == "1":
            input_id = input("Input match id: ")
            load_match_details(item_id=input_id)
        elif load_match_operation == "2":
            count_hours = input("Input count of hours: ")
            load_match_details(hour=int(count_hours))
    elif operation == "4":
        input_platform = input("Input platform: ")
        input_tier = input("Input tier: ")
        if input_tier:
            in_tier = int(input_tier)
        else:
            in_tier = 0

        input_division = input("Input division: ")
        if input_division:
            in_division = int(input_division)
        else:
            in_division = 0

        input_count_pages = input("Input count pages: ")
        if input_count_pages:
            in_count_pages = int(input_count_pages)
        else:
            in_count_pages = 10000

        load_summoner_list(platform_param=input_platform,
                           tier_param=in_tier,
                           division_param=in_division,
                           count_pages=in_count_pages)
