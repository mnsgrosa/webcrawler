from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from src.utils.logger import MyLogger
from datetime import datetime
from contextlib import contextmanager
from src.orchestrate.crawler.abstract_tool import MyCrawler
import re
import httpx
import json
import time

class MyPlaystationCrawler(MyCrawler):
    '''
    Classe responsavel pelo scraping de ofertas da playstation store
    '''
    def __init__(self):
        super().__init__(__name__)
        self.platform = 'playstation'
        self.base_url = 'https://store.playstation.com/pt-br/pages/deals/'
        self.url = self.base_url
        self.games_list = []

    @contextmanager
    def get_webdriver(self):
        driver = None
        try:
            self.logger.info('Creating playstation driver')
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage") 
            chrome_options.add_argument('--max-connections-per-host=2')
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

    def get_deals_page(self):
        with self.get_webdriver() as driver:
            try:
                self.logger.info('Waiting playstation page to load')
                view_all_selector = "//a[.//span[starts-with(@id, 'view-all-')]]"
                view_all_button = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, view_all_selector))
                )
                view_all_button.click()
                self.logger.info(f'View all button clicked, redirecting to {driver.current_url}')
                self.url = driver.current_url
                return self.url
            except Exception as e:
                self.logger.error(f'Couldnt get to deals page: {e}', exc_info = True)
                return None

    def get_contents(self):
        if self.url == self.base_url:
            self.logger.info('Still at the first page: run get_contents()')
            return []
        with self.get_webdriver() as driver:
            try:
                self.logger.info('Starting scrapping from deals page')
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                games = soup.find('ul', class_ = 'psw-grid-list')
                self.logger.info('Deals grid found starting to scrape titles')
                titles = games.find_all('li')
                self.logger.info(f'Type of titles: {type(titles)}')
                self.logger.info(f'Found {len(titles)} titles')
                date = datetime.now().date()
                for i, title in enumerate(titles):
                    self.logger.info(f'Title {i + 1} of {len(titles)}')
                    self.logger.info(f'Title: {title.get_text(strip = True)}')
                    game_name = title.find('span', {'data-qa': lambda x: x and 'product-name' in x})
                    game_name_text = game_name.get_text(strip = True) if game_name else None 
                    self.logger.info(f'Game name: {game_name_text}')
                    game_type = title.find('span', {'data-qa': lambda x: x and 'product-type' in x})
                    game_type_text = game_type.get_text(strip = True) if game_type else 'standard'
                    self.logger.info(f'Game type: {game_type_text}')
                    discount_price = title.find('span', {'data-qa': lambda x: x and 'price' in x})
                    discount_price_text = discount_price.get_text(strip = True) if discount_price else 0
                    if discount_price_text != 0:
                        discount_price_text = re.findall(r'\d+\,\d+', discount_price_text)
                        discount_price_text = discount_price_text[0].replace(',', '.')
                    self.logger.info(f'Discount price: {discount_price_text}')
                    self.games_list.append({
                        'date': date.isoformat(),
                        'platform': self.platform,
                        'game_name': game_name_text,
                        'game_type': game_type_text,
                        'price': discount_price_text
                    })
                self.logger.info(f'Scrapping finished from deals page: {self.games_list}')
                return self.games_list
            except Exception as e:
                self.logger.error(f'Couldnt get deals: {e}')
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
        self.logger.info('Starting the playstation process')
        if self.url != self.base_url:
            self.logger.error('Not located at the base page')
            self.url = self.base_url
            return []
        
        self.get_deals_page()
        self.get_contents()
        self.post_contents()
        self.logger.info('Playstation scraping done')