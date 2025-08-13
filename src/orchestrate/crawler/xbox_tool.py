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
from src.crawler.abstract_tool import MyCrawler
from datetime import datetime
from contextlib import contextmanager
import re
import httpx
import json
import time

class MyXboxCrawler(MyCrawler):
    def __init__(self):
        super().__init__(__name__)
        self.platform = 'xbox'
        self.url = 'https://www.microsoft.com/pt-br/store/deals/games/xbox'
        self.firefox_options = Options()
        self.firefox_options.add_argument("--headless")
        self.games_list = []
    
    @contextmanager
    def get_webdriver(self):
        driver = None
        try:
            if driver is None: 
                self.logger.info('Creating xbox driver')
                driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options = self.firefox_options)
                self.logger.info(f'Driver created and navigating {self.url}')
                driver.get(self.url)
                yield driver
        except Exception as e:
            self.logger.error(f'An error ocurred: {e} @ {self.url}')
        finally:
            if driver:
                driver.quit()
                self.logger.info('Driver closed')

    def get_deals(self):
        if self.url != self.base_url:
            self.logger.error('Not located at the base page')
            return []

        with self.get_webdriver() as driver:
            try:
                self.logger.info('Starting to get xbox deals')
                wait = WebDriverWait(driver, 5)
                wait.until(EC.presence_of_element_located((By.ID, 'productListDetailsWrapper')))
                self.logger.info('Element loaded')
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                self.logger.info('Soup created from deals page')
                deals_grid = soup.find(id = 'productListDetailsWrapper')
                if not deals_grid:
                    self.logger.error('Couldnt find the grid even waiting')
                    return []
                titles = deals_grid.find_all('li', class_ = 'col mb-4 px-2')
                self.logger.info(f'Found {len(titles)} titles')
                for i, title in enumerate(titles):
                    self.logger.info(f'Getting title:{i + 1} of {len(titles)}')
                    game_name = title.find('a', attrs = {'aria-label': True}).get_text(strip = True)
                    self.logger.info(f'Getting the game name: {game_name}') 
                    discount_price = title.find('span', class_ = 'font-weight-semibold').get_text(strip = True)
                    discount_price = re.findall(r'\d+\,\d+', discount_price)
                    if discount_price:
                        discount_price = discount_price[0].replace(',', '.')
                        self.logger.info(f'Getting the discount price: {discount_price}')
                        date = datetime.now().date()
                        self.games_list.append({
                            'date': date,
                            'platform': self.platform,
                            'game_name': game_name,
                            'game_type': 'standard',
                            'price': discount_price
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

    def full_process(self):
        self.logger.info('Starting the xbox process')
        self.get_deals()
        self.post_contents()
        self.logger.info('Xbox scraping done')