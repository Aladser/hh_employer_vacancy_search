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
    vacancies_list = hh_api.load_vacancies(employers_list)
    # db_manager.init(employers_list)
    db_manager.remove_vacancies()

    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()
    # добавление вакансии в БД
    for vcn in vacancies_list:
        # пропуск вакансий без указанной зарплаты
        if vcn['salary'] is None:
            continue

        # объект вакансии
        db_vacancy = {
            'id': int(vcn['id']),
            'name': vcn['name'],
            'salary_from': vcn['salary']['from'],
            'salary_to': vcn['salary']['to'],
            'salary_currency': vcn['salary']['currency'],
            'employer_id': int(vcn['employer']['id']),
            'url': vcn['alternate_url']}

        # добавление в БД
        query = (f"insert into {SCHEMA_NAME}.vacancies ("
                 f"vacancy_id, vacancy_name, "
                 f"employer_id, "
                 f"vacancy_url, "
                 f"vacancy_salary_currency,")

        if db_vacancy['salary_from'] and db_vacancy['salary_to']:
            query += 'vacancy_salary_from, vacancy_salary_to '
        elif db_vacancy['salary_from']:
            query += 'vacancy_salary_from '
        else:
            query += 'vacancy_salary_to '

        query += (f") values ("
                  f"{db_vacancy['id']}, '{db_vacancy['name']}', "
                  f"{db_vacancy['employer_id']}, "
                  f"'{db_vacancy['url']}', "
                  f"'{db_vacancy['salary_currency']}', ")

        if db_vacancy['salary_from'] and db_vacancy['salary_to']:
            query += f"{db_vacancy['salary_from']}, {db_vacancy['salary_to']}"
        elif db_vacancy['salary_from']:
            query += f"{db_vacancy['salary_from']}"
        else:
            query += f"{db_vacancy['salary_to']}"

        query += ") returning *"
        cursor.execute(query)

    conn.commit()
    cursor.close()
    conn.close()
