import psycopg2

from src.api import HHApi
from src import DBManager

SCHEMA_NAME = 'public'
CONFIG_FILENAME = 'env'
EMPLOYERS_FILENAME = 'employers'

# -----БД СОЕДИНЕНИЕ-----
conn_params = {}
with open(CONFIG_FILENAME, 'r') as file:
    for line in file:
        key, value = line.split(':')
        value = value.replace('\n', '')
        conn_params[key] = value

# -----СПИСОК КОМПАНИЙ-РАБОТОДАТЕЛЕЙ ИЗ ФАЙЛА-----
employers_list = []
with open(EMPLOYERS_FILENAME, 'r') as file:
    for line in file:
        id, name = line.split(':')
        name = name.replace('\n', '')
        employers_list.append({'id': int(id), 'name': name})

hh_api = HHApi()
db_manager = DBManager(**conn_params)

if __name__ == '__main__':
    # db_manager.init(employers_list)
    db_manager.remove_vacancies()

    vacancies_list = hh_api.load_vacancies(employers_list)
    db_manager.load_vacancies(vacancies_list)
