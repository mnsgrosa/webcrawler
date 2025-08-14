from abc import ABC, abstractmethod
from src.utils.logger import MyLogger

class MyCrawler(ABC, MyLogger):
    '''
    Classe abstrata dos crawlers:
    Obriga cada crawler a ter o metodo de contexto do webdriver
    '''
    @abstractmethod
    def get_webdriver(self):
        pass

