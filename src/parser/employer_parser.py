from src.parser.basic_file_parser import BasicFileParser


class EmployerParser(BasicFileParser):
    @staticmethod
    def parse(filepath):
        """парсит файл компаний-работодателей"""
        employers_list = []
        with open(filepath, 'r') as file:
            for line in file:
                id, name = line.split(':')
                name = name.replace('\n', '')
                employers_list.append({'id': int(id), 'name': name})
        return employers_list
