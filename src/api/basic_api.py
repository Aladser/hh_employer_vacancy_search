from abc import ABC, abstractmethod


class BasicApi(ABC):
    @abstractmethod
    def load_vacancies(self, keyword) -> None:
        pass
