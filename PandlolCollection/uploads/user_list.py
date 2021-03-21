from PandlolCollection import db


class UserUploader:
    def __init__(self):
        self.user_list = db.user_list

    def get_url(self, platform: str, queue: str, tier: str, division: str):
        pass

    def get_list(self, page_num: int):
        """
        Метод получает список пользователей с указанной страницы
        :param page_num: Номер страницы
        :return: Количество записей
        """
        return page_num

    def upload_list(self, page_num):
        """
        Метод загружает страницу со списком призывателей в БД
        :param page_num: Номер страницы
        :return: Количество загруженных записей
        """
        records_count = self.get_list(page_num)

        result = self.user_list.update_many()
        return result.modified_count
