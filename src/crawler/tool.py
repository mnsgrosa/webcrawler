from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from logger import MyLogger
import json
import time


class MyCrawler(MyLogger):
    def __init__(self, platform: str = 'playstation'):
        super().__init__()
        options = {'playstation': 'https://store.playstation.com/pt-br/pages/deals/',
                'xbox': 'https://www.xbox.com/pt-BR/promotions/sales/sales-and-specials',
                'steam': 'https://store.steampowered.com/specials/?l=portuguese'}
        self.platform = platform
        self.url = options[platform]
        firefox_options = Options()
        firefox_options.add_argument("--headless")

        self.logger.info('Creating the driver')
        self.driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options = firefox_options)
        self.logger.info('Driver created')
        self.logger.info(f'Entering the base page:{self.url}')
        self.driver.get(self.url)
        self.logger.info('Base page entered')

        self.games_list = {}

    def get_all_deals_page(self):
        if self.platform == 'playstation':
            try:
                self.logger.info('Waiting playstation page to load')
                view_all_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-qa='ems-sdk-strand#viewMore#tabletAndAbove']"))
                )
                self.logger.info('View all button found')
                view_all_button.click()
                self.logger.info('View all button clicked, waiting for page to load')
                time.sleep(10)
                self.logger.info('Element found')
                return self.driver.page_source
            except Exception as e:
                pass
        elif self.platform == 'xbox':
            pass
        elif self.platform == 'steam':
            pass
        
        return self.driver.page_source

    def get_contents(self):
        if self.platform == 'playstation':
            if 'deals' in self.driver.current_url:
                self.logger.info('Deals page not initialized')
                return 'Run get_all_deals_page() first'
            try:
                self.logger.info('Starting scrapping from deals page')
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                self.logger.info('Scrapping finished from deals page. Starting to scrape grid list')
                games = soup.find('ul', class_ = 'psw-grid-list')
                self.logger.info('Deals grid found starting to scrape titles')
                titles = games.find_all('li')
                self.logger.info(f'Found {len(titles)} titles')
                self.logger.info(f'Type of titles: {type(titles)}')
                for title in titles:
                    self.logger.info(f'Title: {title.get_text(strip = True)}')
                    game_name = title.find('span', {'data-qa': lambda x: x and 'product-name' in x}).get_text(strip = True)
                    self.logger.info(f'Game name: {game_name}')
                    game_type = title.find('span', {'data-qa': lambda x: x and 'product-type' in x}).get_text(strip = True)
                    self.logger.info(f'Game type: {game_type}')
                    discount_price = title.find('span', {'data-qa': lambda x: x and 'price' in x}).get_text(strip = True)
                    self.logger.info(f'Discount price: {discount_price}')
    
                    self.logger.info(f'Starting to scrape platforms')
                    platforms = [tag.get_text(strip=True) for tag in title.find_all('span', class_='psw-platform-tag')]
                    self.logger.info(f'Platforms: {platforms}')
                    self.games_list[game_name] = {
                        'game_type': game_type,
                        'discount_price': discount_price,
                        'platforms': platforms
                    }
                    return self.games_list
            except Exception as e:
                self.logger.error(f'Couldnt get deals:{e}')