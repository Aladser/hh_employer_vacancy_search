from src.parser.basic_file_parser import BasicFileParser


class ConfigParser(BasicFileParser):
    @staticmethod
    def parse(abs_filepath):
        """парсит файлы-конфиги"""
        params = {}
        with open(abs_filepath, 'r') as file:
            for line in file:
                key, value = line.split(':')
                value = value.replace('\n', '')
                params[key] = value
        return params

