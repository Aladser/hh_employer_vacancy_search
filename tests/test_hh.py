import pytest
from src.api import HHApi


@pytest.fixture
def params():
    return {
        'order_by': 'salary_desc',  # по убыванию зарплаты
        'area': 113,  # вся Россия
        'page': 0,
        'per_page': 25,
        'employer_id': 4181,
        'text': ''
    }


def test_work(params):
    api = HHApi()
    vacancies_list = api.load_vacancies([{'id': 3529, 'name': 'Сбер'}],'менеджер')
    assert len(vacancies_list) == 25
    api = HHApi(1, 25, params)
    assert len(vacancies_list) == 25
    assert api.params == 'order_by:salary_desc, area:113, page:0, per_page:25, employer_id:4181, text:'