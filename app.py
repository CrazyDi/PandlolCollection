from pymongo import MongoClient

from config import Config
from PandlolCollection.LoaderTier import LoaderTier
from PandlolCollection.constant import PLATFORM, TIER, DIVISION


if __name__ == '__main__':
    # открываем соединение
    nosql_connector = MongoClient(Config.NOSQL_CONNECTION_STRING)

    platform_list = PLATFORM
    tier_list = TIER

    for platform in platform_list:
        for tier in tier_list:
            # Для низкого эло
            if tier < 10:
                division_list = DIVISION
            else:  # для высого это рангов нет, возьмем только один
                division_list = {1: "I"}

            for division in division_list:
                loader_tier = LoaderTier(
                    nosql_connection=nosql_connector,
                    record={
                        "platform": platform,
                        "tier": tier,
                        "division": division,
                        "queue": 420
                    }
                )
                #loader_tier.load_max_tier_page()
                loader_tier.load_random_match_list()

    # закрываем соединение
    nosql_connector.close()
