import requests
from src.api.basic_api import BasicApi


class HHApi(BasicApi):
    """
        Класс для работы с API HeadHunter -
        подключается к HeadHunter и возвращает список найденных вакансий
    """

    __url = 'https://api.hh.ru/vacancies'
    __headers = {'User-Agent': 'HH-User-Agent'}
    __page_count: int
    __per_page: int
    __params: dict

    def __init__(self, page_count=1, per_page=30, params=None):
        self.__page_count = page_count
        """число страниц"""
        self.__per_page = per_page
        """число вакансий на странице"""
        if params is None:
            self.__params = {
                'page': 0,
                'per_page': self.__per_page,
                'order_by': 'salary_desc',  # по убыванию зарплаты
                'area': 113,  # Вся Россия
                'text': ''
            }
        else:
            self.__params = params

    def load_vacancies(self, keyword="") -> list:
        pass

    @property
    def params(self) -> str:
        return ', '.join([f"{key}:{value}" for key, value in self.__params.items()])
