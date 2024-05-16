import psycopg2
import requests

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

# -----СПИСОК КОМПАНИЙ-РАБОТОДАТЕЛЕЙ-----
employers_list = []
with open(EMPLOYERS_FILENAME , 'r') as file:
    for line in file:
        id, name = line.split(':')
        name = name.replace('\n', '')
        employers_list.append({'id': int(id), 'name': name})


if __name__ == '__main__':
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()

    # -----запрос на api.hh.ru-----
    url = 'https://api.hh.ru/vacancies'
    headers = {'User-Agent': 'HH-User-Agent'}
    page_count = 1
    params = {
        'order_by': 'salary_desc',
        'area': 113,
        'page': 0,
        'per_page': 30,
        'text': ''
    }

    vacancies_obj_list = []
    params['text'] = 'php разработчик'
    while params['page'] != page_count:
        response = requests.get(url, headers=headers, params=params)
        resp_vacancies = response.json()['items']
        vacancies_obj_list.extend(resp_vacancies)
        params['page'] += 1
