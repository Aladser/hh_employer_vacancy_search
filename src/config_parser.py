class ConfigParser:
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

