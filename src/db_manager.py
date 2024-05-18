import psycopg2


class DBManager:
    """Взаимодействие с БД"""

    __schema_name = 'public'
    __conn_params: dict

    def __init__(self, host: str, port: int, dbname: str, user: str, password: str):
        self.__conn_params = {
            'host': host,
            'port': port,
            'dbname': dbname,
            'user': user,
            'password': password
        }

        self.__conn = None
        self.__cursor = None

    def connect(self):
        """подключается к БД"""

        self.__conn = psycopg2.connect(**self.__conn_params)
        self.__cursor = self.__conn.cursor()

    def disconnect(self):
        """отключается от БД"""

        self.__conn.commit()
        self.__cursor.close()
        self.__conn.close()
        self.__conn = None
        self.__cursor = None

    def recreate_tables(self, employers_list: list) -> None:
        """Пересоздает таблицы БД"""

        self.connect()
        self.__cursor.execute(f"create schema if not exists {self.__schema_name};")
        self.__cursor.execute(f"DROP TABLE IF EXISTS {self.__schema_name}.vacancies")
        self.__cursor.execute(f"DROP TABLE IF EXISTS {self.__schema_name}.employers")

        # -----Работодатели-----
        self.__cursor.execute(f"create table {self.__schema_name}.employers("
                              f"employer_id bigint primary key,"
                              f"employer_name varchar(255) not null"
                              f")")

        # -----Вакансии-----
        self.__cursor.execute(f"create table {self.__schema_name}.vacancies("
                              f"vacancy_id bigint primary key,"
                              f"vacancy_name varchar(255) not null,"
                              f"vacancy_url varchar(255),"
                              f"vacancy_salary_from integer,"
                              f"vacancy_salary_to integer,"
                              f"vacancy_salary_currency varchar(10),"
                              f"employer_id bigint references {self.__schema_name}.employers(employer_id)"
                              f")")

        # -----заполнение таблицы Работодатели-----
        for employer in employers_list:
            query = (f"insert into {self.__schema_name}.employers (employer_id, employer_name) "
                     f"values({employer['id']}, '{employer['name']}') returning *")
            self.__cursor.execute(query)

        self.disconnect()

    def load_vacancies(self, vacancies_list: list):
        """загружает вакансии в БД"""

        self.connect()
        # добавление вакансий в БД
        for vacancy in vacancies_list:
            # пропуск вакансий без указанной зарплаты
            if vacancy['salary'] is None:
                continue

            # объект вакансии
            db_vacancy = {
                'id': int(vacancy['id']),
                'name': vacancy['name'],
                'salary_from': vacancy['salary']['from'],
                'salary_to': vacancy['salary']['to'],
                'salary_currency': vacancy['salary']['currency'],
                'employer_id': int(vacancy['employer']['id']),
                'url': vacancy['alternate_url']}

            # добавление в БД
            query = (f"insert into {self.__schema_name}.vacancies ("
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
            self.__cursor.execute(query)

        self.disconnect()

    def remove_vacancies(self):
        """Удаляет вакансии из БД"""

        self.connect()
        self.__cursor.execute(f"delete from {self.__schema_name}.vacancies")
        self.disconnect()

    def get_companies_and_vacancies_count(self):
        """получает список всех компаний и количество вакансий у каждой компании"""

        self.connect()
        query = (f"select employer_name, count(*) as count "
                 f"from {self.__schema_name}.vacancies join {self.__schema_name}.employers using (employer_id)"
                 f"group by employer_name")
        self.__cursor.execute(query)
        employments_stat = self.__cursor.fetchall()
        self.disconnect()
        return [{'employer_name': item[0], 'vacancy_count': item[1]} for item in employments_stat]

    def get_all_vacancies(self):
        """получает список всех вакансий"""

        self.connect()
        query = (f"select vacancy_name, "
                 f"vacancy_salary_from, vacancy_salary_to, vacancy_salary_currency, "
                 f"employer_name, vacancy_url from {self.__schema_name}.vacancies "
                 f"join {self.__schema_name}.employers using (employer_id)")
        self.__cursor.execute(query)
        raw_vacancies_list = self.__cursor.fetchall()
        self.disconnect()

        return self.__get_formatted_vacancies(raw_vacancies_list)

    def get_avg_salary(self) -> dict:
        """
        получает среднюю начальную зарплату по вакансиям
        :return: {величина, валюта}
        """

        self.connect()
        query = "select avg(vacancy_salary_from) from vacancies where vacancies.vacancy_salary_currency = 'RUR'"
        self.__cursor.execute(query)
        avg_salary = self.__cursor.fetchall()
        self.disconnect()
        return {'value': int(avg_salary[0][0]), 'currency': 'RUR'}

    def get_vacancies_with_higher_salary(self):
        """получает список всех вакансий, у которых зарплата выше средней по всем вакансиям."""

        self.connect()
        query = ("select vacancy_name,"
                 "vacancy_salary_from, vacancy_salary_to, vacancy_salary_currency,"
                 "employer_name, vacancy_url from vacancies join employers using (employer_id) "
                 "where vacancy_salary_from > ("
                 "  select avg(vacancy_salary_from) from vacancies where vacancies.vacancy_salary_currency = 'RUR'"
                 ") and vacancy_salary_currency = 'RUR'")
        self.__cursor.execute(query)
        raw_vacancies_list = self.__cursor.fetchall()
        self.disconnect()

        return self.__get_formatted_vacancies(raw_vacancies_list)

    def get_vacancies_with_keyword(self, keyword=""):
        """ получает список всех вакансий, в названии которых содержатся переданные в метод слова"""

        self.connect()
        query = (f"select vacancy_name, "
                 f"vacancy_salary_from, vacancy_salary_to, vacancy_salary_currency, "
                 f"employer_name, vacancy_url from vacancies join employers using (employer_id) "
                 f"where vacancy_name like '%{keyword}%'")
        self.__cursor.execute(query)
        raw_vacancies_list = self.__cursor.fetchall()
        self.disconnect()

        return self.__get_formatted_vacancies(raw_vacancies_list)

    @staticmethod
    def __get_formatted_vacancies(raw_vacancies_list):
        """преобразовать двумерный массив вакансий в массив словарей"""

        vacancies_list = []
        for vcn in raw_vacancies_list:
            # парсинг зарплаты
            if vcn[1] is not None and vcn[2] is not None:
                salary = f"от {vcn[1]} до {vcn[2]} {vcn[3]}"
            elif vcn[1] is not None:
                salary = f"от {vcn[1]} {vcn[3]}"
            elif vcn[2] is not None:
                salary = f"до {vcn[2]} {vcn[3]}"
            else:
                salary = 'не указана'

            vacancies_list.append({
                'vacancy_name': vcn[0],
                'salary': salary,
                'employer_name': vcn[4],
                'vacancy_url': vcn[5]
            })

        return vacancies_list

    @staticmethod
    def print_vacancy(vcn) -> None:
        """форматированная печать вакансии"""
        print(f"Название: {vcn['vacancy_name']}\n"
              f"Зарплата: {vcn['salary']}\n"
              f"Компания: {vcn['employer_name']}\n"
              f"Ссылка на вакансию: {vcn['vacancy_url']}\n"
              )
