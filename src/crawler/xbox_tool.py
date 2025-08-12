from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from src.utils.logger import MyLogger
from datetime import datetime
import httpx
import json
import time

class MyXboxCrawler(MyLogger):
    def __init__(self):
        super().__init__()
        self.platform = 'xbox'
        self.url = 'https://www.microsoft.com/pt-br/store/deals/games/xbox'
        firefox_options = Options()
        firefox_options.add_argument("--headless")

        self.logger.info('Creating the Xbox driver')
        self.driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options = firefox_options)
        self.logger.info('Driver created')
        self.logger.info(f'Entering the base page:{self.url}')
        self.driver.get(self.url)
        self.logger.info('Base page entered')

        self.games_list = []
    
    def get_deals(self):
        try:
            self.logger.info('Starting to get xbox deals')
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            self.logger.info('Soup created from deals page')
            deals_grid = soup.find('ProductListDetailsWrapper')
            self.logger.info('Deals grid found')
            self.logger.info(f'Grid object type: {type(deals_grid)} and length: {len(deals_grid)}')
            titles = deals_grid.find_all('li', class_ = 'col mb-4 px-2')
            self.logger.info(f'Found {len(titles)} titles')
            game_names = titles.find_all('a', attrs = {'aria-label': True})
            self.logger.info('Getting the discounted prices')
            discount_prices = titles.find_all('span', class_ = 'font-weight-semibold')
            date = datetime.now().date()
            for name, discount_price in zip(game_names, discount_prices):
                self.logger.info('Creating the xbox game list')
                self.games_list.append({
                    'date': date,
                    'platform': self.platform,
                    'game_name': name.get_text(strip = True),
                    'game_type': 'standard',
                    'price': discount_price.get_text(strp = True)
                })
            self.logger.info('Scrapping finished from deals page')
            return self.games_list
        except Exception as e:
            self.logger.error(f'Couldnt get xbox deals: {e}')
            return []

    def post_contents(self):
        self.logger.info('Starting post method')
        if self.games_list is None:
            self.logger.info('Get the deals first')
            return {}
        try:
            self.logger.info('Starting to post the deals')
            with httpx.Client() as client:
                response = client.post('http://localhost:8000/post/games', json = self.games_list)
                response.raise_for_status()
            self.logger.info(f"Deals posted: {response.json().get('status')}")
            return response.json()
        except Exception as e:
            self.logger.error(f'Failed to post deals: {e}')
            return {}