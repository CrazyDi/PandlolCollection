from PandlolCollection import db


if __name__ == '__main__':
    test = db.test

    test_id = test.insert_one({"code": "1", "name": "test1"}).inserted_id
    print(test_id)
