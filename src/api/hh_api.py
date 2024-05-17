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
    __params: dict

    def __init__(self, page_count: int = 1, per_page: int = 25, params: dict = None):
        self.__page_count = page_count
        """число вакансий на странице"""
        if params is None:
            self.__params = {
                'order_by': 'salary_desc', # по убыванию зарплаты
                'area': 113, # вся Россия
                'page': 0,
                'per_page': per_page,
                'employer_id': "",
                'text': ''
            }
        else:
            self.__params = params

    def load_vacancies(self, employers_list: list, keyword="") -> list:
        """ Запрос вакансий на api.hh.ru """

        vacancies_list = []
        self.__params['text'] = keyword

        # запрос вакансий
        for employer in employers_list:
            self.__params['page'] = 0
            self.__params['employer_id'] = employer['id']
            while self.__params['page'] != self.__page_count:
                response = requests.get(self.__url, headers=self.__headers, params=self.__params)
                resp_vacancies = response.json()['items']
                vacancies_list.extend(resp_vacancies)
                self.__params['page'] += 1

        return vacancies_list

    @property
    def params(self) -> str:
        return ', '.join([f"{key}:{value}" for key, value in self.__params.items()])
