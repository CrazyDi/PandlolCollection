from pymongo import MongoClient

from config import Config


if __name__ == "__main__":
    client = MongoClient(Config.NOSQL_CONNECTION_STRING)
    db = client.pandlol
    match_detail_table = db.match_detail
    match_state_table = db.match_state

    early_surr_match = match_detail_table.find({'early_surr': True}).distinct("match_id")
    print(len(early_surr_match))

    for match in early_surr_match:
        print(match)
        match_state_table.delete_many({"match_id": match})
        match_detail_table.delete_many({"match_id": match})
