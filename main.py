import os.path

from src import DBManager
from src.api import HHApi
from src import ConfigParser

root_dir = os.path.dirname(os.path.abspath(__file__))

# -----БД СОЕДИНЕНИЕ-----
conn_params = ConfigParser.parse(root_dir+'/env')
db_manager = DBManager(**conn_params)

# -----СПИСОК КОМПАНИЙ-РАБОТОДАТЕЛЕЙ ИЗ ФАЙЛА-----
EMPLOYERS_FILENAME = 'employers'
employers_list = []
with open(EMPLOYERS_FILENAME, 'r') as file:
    for line in file:
        id, name = line.split(':')
        name = name.replace('\n', '')
        employers_list.append({'id': int(id), 'name': name})

hh_api = HHApi()


if __name__ == '__main__':
    db_manager.recreate_tables(employers_list)
    vacancies_list = hh_api.load_vacancies(employers_list)
    db_manager.load_vacancies(vacancies_list)


    print('/// Cписок всех компаний и количество вакансий у каждой компании ///')
    vacancies_data = db_manager.get_companies_and_vacancies_count()
    print('Компания | число вакансий')
    for vcn in vacancies_data:
        print(f"{vcn['employer_name']} | {vcn['vacancy_count']}")
    print('---------------------------\n')


    print('/// Cписок всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию ///')
    vacancies_data = db_manager.get_all_vacancies()
    for i in range(3):
        [print(f"{k}: {v}") for k,v in vacancies_data[i].items()]
        print()
    print('---------------------------\n')


    print('/// Средняя зарплата по вакансиям: ///', end=' ')
    avg_price = db_manager.get_avg_salary()
    print(f"{avg_price['value']} {avg_price['currency']}")
    print('---------------------------\n')


    print('/// список всех вакансий, у которых зарплата выше средней по всем вакансиям ///')
    vacancies_data = db_manager.get_vacancies_with_higher_salary()
    for i in range(5):
        [print(f"{k}: {v}") for k,v in vacancies_data[i].items()]
        print()
    print('---------------------------\n')


    print('/// список всех вакансий, в названии которых содержатся переданные в метод слова, например Менеджер ///')
    vacancies_data = db_manager.get_vacancies_with_keyword('Менеджер')
    for i in range(5):
        [print(f"{k}: {v}") for k,v in vacancies_data[i].items()]
        print()
    print('---------------------------\n')
