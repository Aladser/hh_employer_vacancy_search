import psycopg2


class DBManager:
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

    def init(self, employers_list: list) -> None:
        """Создает таблицы БД"""

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

    def remove_vacancies(self):
        """Удаляет вакансии из БД"""
        self.connect()
        self.__cursor.execute(f"delete from {self.__schema_name}.vacancies")
        self.disconnect()
