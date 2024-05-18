import os.path

from src.api import HHApi
from src import DBManager
from src.parser import ConfigParser, EmployerParser

root_dir = os.path.dirname(os.path.abspath(__file__))
# соединение с БД
conn_params = ConfigParser.parse(root_dir+'/env')
db_manager = DBManager(**conn_params)
# список компаний-работодателей
employers_list = EmployerParser.parse(root_dir+'/employers')
# HHApi
hh_api = HHApi()

if __name__ == '__main__':
    db_manager.recreate_tables(employers_list)
    vacancies_list = hh_api.load_vacancies(employers_list)
    db_manager.load_vacancies(vacancies_list)


    print('/// -----Cписок всех компаний и количество вакансий у каждой компании----- ///')
    vacancies_data = db_manager.get_companies_and_vacancies_count()
    [print(f"{vcn['employer_name']}: {vcn['vacancy_count']} вакансий") for vcn in vacancies_data]
    print('---------------------------\n')


    print('/// -----Cписок всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию----- ///')
    vacancies_data = db_manager.get_all_vacancies()
    for i in range(3):
        DBManager.print_vacancy(vacancies_data[i])
        print()
    print('---------------------------\n')

    avg_price = db_manager.get_avg_salary()
    print(f"/// -----Средняя зарплата по вакансиям: {avg_price['value']} {avg_price['currency']}-----///")
    print('---------------------------\n')

    print('/// -----Cписок всех вакансий, у которых зарплата выше средней по всем вакансиям---- ///')
    vacancies_data = db_manager.get_vacancies_with_higher_salary()
    for i in range(5):
        DBManager.print_vacancy(vacancies_data[i])
        print()
    print('---------------------------\n')


    print('/// -----Cписок всех вакансий, в названии которых содержатся переданные в метод слова, например Менеджер----- ///')
    vacancies_data = db_manager.get_vacancies_with_keyword('Менеджер')
    for i in range(5):
        DBManager.print_vacancy(vacancies_data[i])
        print()
    print('---------------------------\n')
