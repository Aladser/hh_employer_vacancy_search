import os.path
import pytest
from src import DBManager
from src.api import HHApi


@pytest.fixture
def conn_params():
    # путь до env
    abs_path = os.path.dirname(os.path.abspath(__file__))
    ENV_PATH = os.path.dirname(abs_path) + '/env'

    # конфиги
    conn_params = {}
    with open(ENV_PATH, 'r') as file:
        for line in file:
            key, value = line.split(':')
            value = value.replace('\n', '')
            conn_params[key] = value
    return conn_params


@pytest.fixture
def employments():
    # путь до employers
    abs_path = os.path.dirname(os.path.abspath(__file__))
    EMPLOYERS_FILENAME = os.path.dirname(abs_path) + '/employers'

    employers_list = []
    with open(EMPLOYERS_FILENAME, 'r') as file:
        for line in file:
            id, name = line.split(':')
            name = name.replace('\n', '')
            employers_list.append({'id': int(id), 'name': name})
    return employers_list


@pytest.fixture
def url_vacancies(employments):
    hh_api = HHApi()
    return hh_api.load_vacancies(employments)


@pytest.fixture
def db_manager(conn_params, employments):
    db_manager = DBManager(**conn_params)
    db_manager.init(employments)
    return db_manager


def test_work(db_manager, url_vacancies):
    db_manager.remove_vacancies()
    db_manager.load_vacancies(url_vacancies)

    db_manager.get_companies_and_vacancies_count()
    db_manager.get_all_vacancies()
    db_manager.get_avg_salary()
    db_manager.get_vacancies_with_higher_salary()
    db_manager.get_vacancies_with_keyword()
