from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from src.utils.logger import MyLogger
from src.orchestrate.crawler.abstract_tool import MyCrawler
from datetime import datetime
from contextlib import contextmanager
import re
import httpx
import json
import time

class MyXboxCrawler(MyCrawler):
    def __init__(self):
        '''
        Classe responsavel por fazer scraping da pagina microsoft store
        '''
        super().__init__(__name__)
        self.platform = 'xbox'
        self.url = 'https://www.microsoft.com/pt-br/store/deals/games/xbox'
        self.games_list = []
    
    @contextmanager
    def get_webdriver(self):
        driver = None
        try:
            self.logger.info('Creating xbox driver')
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage") 
            driver = webdriver.Chrome(
                options=chrome_options
            )

            self.logger.info(f'Driver created and navigating to {self.url}')
            driver.get(self.url)
            yield driver

        finally:
            if driver:
                driver.quit()
                self.logger.info('Driver closed')

    def get_deals(self):
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
                            'date': date.isoformat(),
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
                response = client.post('http://api:9000/post/games', json = {'items':self.games_list})
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