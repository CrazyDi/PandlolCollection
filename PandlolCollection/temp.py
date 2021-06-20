from pymongo import MongoClient

from config import Config


if __name__ == "__main__":
    client = MongoClient(Config.NOSQL_CONNECTION_STRING)
    db = client.pandlol
    match_event_table = db.match_event
    match_detail_table = db.match_detail

    event_begin_end_table = db.event_begin_end
    event_begin_end_table.drop()

    event_building_table = db.event_building
    event_building_table.drop()

    event_champion_table = db.event_champion
    event_champion_table.drop()

    event_monster_table = db.event_monster
    event_monster_table.drop()

    event_dragon_soul_table = db.event_dragon_soul
    event_dragon_soul_table.drop()

    event_monster_table = db.event_monster
    event_monster_table.drop()

    event_item_table = db.event_item
    event_item_table.drop()

    event_skill_table = db.event_skill
    event_skill_table.drop()

    event_level_table = db.event_level
    event_level_table.drop()

    event_ward_table = db.event_ward
    event_ward_table.drop()

    match_list = match_detail_table.distinct("match_id")[0:999]

    for match_id in match_list:
        match_detail_list = list(match_detail_table.find({"match_id": match_id}))

        # заполним информацию об участниках матча
        participant_list = {
            participant['participant_code']: {
                "queue": participant['queue'],
                "platform": participant['platform'],
                "patch": participant['patch'],
                "tier": participant['tier'],
                "division": participant['division'],
                "puu_id": participant['puu_id'],
                "champion_name": participant['champion_pick'],
                "team_code": participant["team_code"]
            } for participant in match_detail_list
        }

        event_list = list(match_event_table.find({"match_id": match_id}))

        for event in event_list:
            if event["event_type"] == "MATCH_BEGIN":
                record = {
                    "match_id": match_id,
                    "patch": participant_list[1]["patch"],
                    "queue": participant_list[1]["queue"],
                    "platform": participant_list[1]["platform"],
                    "begin_time": event["event"]["real_timestamp"]
                }

                event_begin_end_table.insert_one(record)

            elif event["event_type"] == "MATCH_END":
                surr = False
                if match_detail_table.find_one({"match_id": match_id, "surr": True}):
                    surr = True

                early_surr = False
                if match_detail_table.find_one({"match_id": match_id, "early_surr": True}):
                    early_surr = True

                record = {
                    "end_time": event["event"]["real_timestamp"],
                    "team_win": event.get("team_code", 0),
                    "duration": event["timestamp"],
                    "surr": surr,
                    "early_surr": early_surr
                }

                event_begin_end_table.update_one({"match_id": match_id}, {"$set": record})

            else:
                participant_code = event.get("participant_code", 0)
                if participant_code > 0:
                    record = {
                        "match_id": match_id,
                        "patch": participant_list[participant_code]["patch"],
                        "queue": participant_list[participant_code]["queue"],
                        "platform": participant_list[participant_code]["platform"],
                        "team_code": participant_list[participant_code]["team_code"],
                        "participant_code": participant_code,
                        "puu_id": participant_list[participant_code]["puu_id"],
                        "champion_name": participant_list[participant_code]["champion_name"],
                        "event_type": event["event_type"],
                        "timestamp": event["timestamp"]
                    }
                else:
                    record = {
                        "match_id": match_id,
                        "patch": participant_list[1]["patch"],
                        "queue": participant_list[1]["queue"],
                        "platform": participant_list[1]["platform"],
                        "team_code": event.get("team_code", 0),
                        "event_type": event["event_type"],
                        "timestamp": event["timestamp"]
                    }

                if event["event_type"] in ['BUILDING_ASSIST', 'BUILDING_KILL', 'TURRET_PLATE_DESTROYED']:
                    if event["event"].get("lane"):
                        record["lane"] = event["event"].get("lane")

                    record["building_type"] = event["event"].get("building_type"),
                    record["turret_type"] = event["event"].get("turret_type")

                    event_building_table.insert_one(record)

                if event["event_type"] in ['CHAMPION_ASSIST', 'CHAMPION_DEATH', 'CHAMPION_KILL']:

                    record["position"] = event["event"]["position"]

                    if event["event"].get("victim_id", event["event"].get("killer_id", 0)) > 0:
                        record["participant_event"] = event["event"].get("victim_id", event["event"].get("killer_id", 0))

                    if event["event"].get("gold_bounty", 0) > 0:
                        record["gold_bounty"] = event["event"].get("gold_bounty", 0)

                    if event["event"].get("kill_streak", 0) > 0:
                        record["kill_streak"] = event["event"].get("kill_streak", 0)

                    if event["event"].get("first_blood", 0) > 0:
                        record["first_blood"] = True

                    if event["event"].get("ace", 0) > 0:
                        record["ace"] = True

                    if event["event"].get("multikill", 0) > 0:
                        record["multikill"] = True

                    event_champion_table.insert_one(record)

                if event["event_type"] == "DRAGON_SOUL_GIVEN":
                    record["soul_type"] = event["event"]["soul_type"]

                    event_dragon_soul_table.insert_one(record)

                if event["event_type"] in ["ELITE_MONSTER_ASSIST", "ELITE_MONSTER_KILL"]:
                    record["monster_type"] = event["event"]["monster_type"]
                    record["monster_sub_type"] = event["event"]["monster_sub_type"]
                    record["position"] = event["event"]["position"]

                    event_monster_table.insert_one(record)

                if event["event_type"] in ["ITEM_DESTROYED", "ITEM_PURCHASED", "ITEM_SOLD"]:
                    record["item_id"] = event["event"]["item_id"]

                    event_item_table.insert_one(record)

                if event["event_type"] == "SKILL_LEVEL_UP":
                    if event["event"].get("skill_code"):
                        record["skill_code"] = event["event"].get("skill_code")
                        event_skill_table.insert_one(record)

                    if event["event"].get("level"):
                        record["event_type"] = "LEVEL_UP"
                        record["level"] = event["event"].get("level")
                        event_level_table.insert_one(record)

                if event["event_type"] in ["WARD_KILL", "WARD_PLACED"]:
                    record["ward_type"] = event["event"]["ward_type"]

                    event_ward_table.insert_one(record)
