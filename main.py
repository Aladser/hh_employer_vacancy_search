import psycopg2

from src.api import HHApi

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

if __name__ == '__main__':
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()

    """
    # -----Создание таблиц-----
    cursor.execute(f"create schema if not exists {SCHEMA_NAME};")
    cursor.execute(f"DROP TABLE IF EXISTS {SCHEMA_NAME}.vacancies")
    cursor.execute(f"DROP TABLE IF EXISTS {SCHEMA_NAME}.employers")

    # -----Работодатели-----
    cursor.execute(f"create table {SCHEMA_NAME}.employers("
                   f"employer_id bigint primary key,"
                   f"employer_name varchar(255) not null"
                   f")")
                   
    # -----Вакансии-----
    cursor.execute(f"create table {SCHEMA_NAME}.vacancies("
                   f"vacancy_id bigint primary key,"
                   f"vacancy_name varchar(255) not null,"
                   f"vacancy_url varchar(255),"
                   f"vacancy_salary_from integer,"
                   f"vacancy_salary_to integer,"
                   f"vacancy_salary_currency varchar(10),"
                   f"employer_id bigint references {SCHEMA_NAME}.employers(employer_id)"
                   f")")

    # -----заполнение таблицы Работодатели-----
    for employer in employers_list:
        query = (f"insert into {SCHEMA_NAME}.employers (employer_id, employer_name) "
                 f"values({employer['id']}, '{employer['name']}') returning *")
        cursor.execute(query)
    """

    cursor.execute(f"delete from {SCHEMA_NAME}.vacancies")
    conn.commit()

    # -----запрос вакансий на api.hh.ru-----
    vacancies_list = hh_api.load_vacancies(employers_list)

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
