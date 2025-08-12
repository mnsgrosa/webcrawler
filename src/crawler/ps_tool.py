from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from src.utils.logger import MyLogger
from datetime import datetime
from contextlib import contextmanager
from src.crawler.abstract_tool import MyCrawler
import httpx
import json
import time

class MyPlaystationCrawler(MyCrawler):
    def __init__(self):
        super().__init__(__name__)
        self.platform = 'playstation'
        self.url = 'https://store.playstation.com/pt-br/pages/deals/'
        self.firefox_options = Options()
        self.firefox_options.add_argument("--headless")
        self.games_list = []

    @contextmanager
    def get_webdriver(self):
        driver = None
        try:
            if driver is None: 
                self.logger.info('Creating playstation driver')
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


    def get_all_deals_page(self):
        with self.get_webdriver() as driver:
            try:
                self.logger.info('Waiting playstation page to load')
                view_all_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-qa='ems-sdk-strand#viewMore#tabletAndAbove']"))
                )
                view_all_button.click()
                self.logger.info(f'View all button clicked, redirecting to {driver.current_url}')
                self.url = driver.current_url
                return self.url
            except Exception as e:
                self.logger.error(f'Couldnt get to deals page: {e}')
                return None

    def get_contents(self):
        if 'deals' in self.url:
            self.logger.info('Deals page not initialized')
            return 'Run get_all_deals_page() first'
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
                    game_type_text = game_type.get_text(strip = True) if game_type else None 
                    self.logger.info(f'Game type: {game_type_text}')
                    discount_price = title.find('span', {'data-qa': lambda x: x and 'price' in x})
                    discount_price_text = discount_price.get_text(strip = True) if discount_price else None 
                    self.logger.info(f'Discount price: {discount_price_text}')
                    self.games_list.append({
                        'date': date,
                        'platform': self.platform,
                        'game_name': game_name_text,
                        'game_type': game_type_text,
                        'price': discount_price_text
                    })
                self.logger.info('Scrapping finished from deals page')
                return self.games_list
            except Exception as e:
                self.logger.error(f'Couldnt get deals: {e}')
                return []

        def post_contents(self):
            self.logger.info('Starting post method')
            if self.game_list is None:
                self.logger.info('Get deals first')
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