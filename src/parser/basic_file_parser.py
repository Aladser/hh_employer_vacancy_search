from abc import ABC, abstractmethod


class BasicFileParser(ABC):
    @staticmethod
    @abstractmethod
    def parse(filepath):
        pass
    