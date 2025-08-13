from abc import ABC, abstractmethod
from src.utils.logger import MyLogger

class MyCrawler(ABC, MyLogger):
    @abstractmethod
    def get_webdriver(self):
        pass

