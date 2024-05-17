import psycopg2
import requests


SCHEMA_NAME = 'public'
CONFIG_FILENAME = 'env'
EMPLOYERS_FILENAME = 'employers'

REQUEST_URL = 'https://api.hh.ru/vacancies'
REQUEST_HEADERS = {'User-Agent': 'HH-User-Agent'}
REQUEST_PAGE_COUNT = 4
REQUEST_PARAMS = {
    'order_by': 'salary_desc',
    'area': 113,
    'page': 0,
    'per_page': 25,
    'employer_id': 3529,
    'text': ''
}

# -----БД СОЕДИНЕНИЕ-----
conn_params = {}
with open(CONFIG_FILENAME, 'r') as file:
    for line in file:
        key, value = line.split(':')
        value = value.replace('\n', '')
        conn_params[key] = value

# -----СПИСОК КОМПАНИЙ-РАБОТОДАТЕЛЕЙ-----
employers_list = []
with open(EMPLOYERS_FILENAME, 'r') as file:
    for line in file:
        id, name = line.split(':')
        name = name.replace('\n', '')
        employers_list.append({'id': int(id), 'name': name})


if __name__ == '__main__':
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()

    """
    # -----Создание таблиц-----
    cursor.execute(f"create schema if not exists {SCHEMA_NAME};")
    cursor.execute(f"DROP TABLE IF EXISTS {SCHEMA_NAME}.employers")
    cursor.execute(f"DROP TABLE IF EXISTS {SCHEMA_NAME}.vacancies")
    # -----работодатели-----
    cursor.execute(f"create table {SCHEMA_NAME}.employers("
                   f"employer_id bigint primary key,"
                   f"employer_name varchar(255) not null"
                   f")")
    # -----вакансии-----
    cursor.execute(f"create table {SCHEMA_NAME}.vacancies("
                   f"worker_id bigint primary key,"
                   f"worker_name varchar(255) not null,"
                   f"worker_salary_from integer,"
                   f"worker_salary_to integer,"
                   f"worker_salary_currency varchar(10),"
                   f"employer_id bigint references {SCHEMA_NAME}.employers(employer_id)"
                   f")")
    """

    conn.commit()
    cursor.close()
    conn.close()

    # -----запрос вакансий на api.hh.ru-----
    vacancies_list = []
    REQUEST_PARAMS['text'] = ''
    # запрос вакансий
    for employer in employers_list:
        REQUEST_PARAMS['page'] = 0
        REQUEST_PARAMS['employer_id'] = employer['id']
        while REQUEST_PARAMS['page'] != REQUEST_PAGE_COUNT :
            response = requests.get(REQUEST_URL, headers=REQUEST_HEADERS, params=REQUEST_PARAMS)
            resp_vacancies = response.json()['items']
            vacancies_list.extend(resp_vacancies)
            REQUEST_PARAMS['page'] += 1
    # удаление вакансий без ЗП
    for vcn in vacancies_list:
        if vcn['salary'] is None:
            vacancies_list.remove(vcn)
    [print(vcn) for vcn in vacancies_list]


