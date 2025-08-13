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

class MySteamCrawler(MyCrawler):
    def __init__(self):
        super().__init__(__name__)
        self.platform = 'pc'
        self.current_url = 'https://store.steampowered.com/'
        self.base_url = self.current_url
        self.firefox_options = Options()
        self.firefox_options.add_argument("--headless")
        self.games_list = []

    @contextmanager
    def get_webdriver(self, url = None):
        driver = None
        try:
            if driver is None: 
                self.logger.info('Creating steam driver')
                driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options = self.firefox_options)
                if url:
                    driver.get(url)
                    self.logger.info(f'Driver created and navigating: {url}')
                else:
                    driver.get(self.current_url)
                    self.logger.info(f'Driver created and navigating: {self.current_url}')
                yield driver
        except Exception as e:
            if url:
                self.logger.error(f'An error ocurred with @ {url}: {e}')
            else:
                self.logger.error(f'An error ocurred: {e} @ {self.current_url}')
        finally:
            if driver:
                driver.quit()
                self.logger.info('Driver closed')

    def get_deals_page(self):
        if self.current_url != self.base_url:
            self.logger.info('Steam page not located at base page: get_deals_url')
            return None
        
        with self.get_webdriver() as driver:
            try:
                self.logger.info('Starting to get steam deal page')
                wait = WebDriverWait(driver, 5)
                specials_button = wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'Specials')))
                self.logger.info('Element loaded')
                specials_button.click()
                self.current_url = driver.current_url
                self.logger.info('Redirected to deals page')
                return self.current_url
            except Exception as e:
                self.logger.error(f'Couldnt get to deals page: {e}')
                return None

    def load_more_deals(self):
        if self.current_url == self.base_url:
            self.logger.error('Still at the homepage: run get_deals_url(): navigate_deals')
        
        self.logger.info('Starting the loop to get 108 games')
        try:
            with self.get_webdriver() as driver:
                for i in range(10):
                    self.logger.info(f'Loop {i + 1} of {10}')
                    self.logger.info('Clicking to show more')
                    show_more_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Show more')]")))
                    show_more_button.click()
                self.current_url = driver.current_url
            return True
        except Exception as e:
            self.logger.error('Couldnt load more deals')
            return False

    def get_deals_appids(self):
        if self.current_url == self.base_url:
            self.logger.info('Still at homepage run: get_deals_url(): get_deals_appids')
            return []
        
        with self.get_webdriver() as driver:
            try:
                self.logger.info('Gathering the deals')
                time.sleep(5)
                self.logger.info('Element loaded')
                soup = BeautifulSoup(driver.page_source, 'html.parser')
            except Exception as e:
                self.logger.error(f'Error couldnt load the page soup: {e}')
                return []
        app_ids = []
        try:
            for div_tag in soup.find_all('div'):
                for attribute_name in div_tag.attrs:
                    if attribute_name.startswith('data-browser_contenthub_all_'):
                        data_string = div_tag[attribute_name]
                        self.logger.info(f'Data string found: {data_string}')
                        data = json.loads(data_string)
                        appids_list = data.get('appids', [])
                        break
            
            if appids_list:
                self.logger.info(f'List of appids: {appids_list} and size: {len(appids_list)}')
                return appids_list
        except Exception as e:
            self.logger.error(f'Couldnt get appids: {e}')
            return []

    def access_appids(self, appids_list):
        if self.current_url == self.base_url:
            self.logger.info('Still at the home page use: get_deals_url(): Access_appids')
            return []

        if appids_list is None:
            self.logger.info(f'Load the appids first: {self.current_url}')
            return []

        self.logger.info('Starting the process of game scraping')
        try:
            for appid in appids_list:
                temp_url = self.base_url + f'app/{appid}/'

                self.logger.info(f'Scraping: {temp_url}')
                try:
                    page = httpx.get(temp_url)
                    page.raise_for_status()
                    soup = BeautifulSoup(page.text, 'html.parser')
                    self.logger.info(f'Soup done')

                    self.logger.info('Getting the game name')
                    game_name = soup.find('div', id = 'appHubAppName').get_text(strip = True)
                    
                    if game_name is None:
                        self.logger.error('Game name not found')
                        return []

                    self.logger.info(f'Game: {game_name}')
                    date = datetime.now().date()
                    discount_price = soup.find('div', class_ = 'discount_final_price').get_text(strip = True)
                    discount_price = re.findall(r'\d+\,\d+', discount_price)
                    if discount_price:
                        discount_price = discount_price[0].replace(',', '.')
                    self.logger.info(f'Price: {discount_price}')

                    self.games_list.append({
                        'date': date,
                        'platform': self.platform,
                        'game_name': game_name,
                        'game_type': 'standard',
                        'price': discount_price
                    })
                except Exception as e:
                    self.logger.error(f'Failed to scrape {appid} due to {e}')
            self.logger.info(f'Size of game list: {len(self.games_list)}')
            return self.games_list
        except Exception as e:
            self.logger.error(f'Failed to scrape games due to: {e}')
            return []

    def full_process(self):
        if self.current_url != self.base_url:
            self.logger.error(f'Returning to the base url located @ {self.current_url}')
            self.current_url = self.base_url
            return []
        
        self.get_deals_page()
        self.load_more_deals()
        appids_list = self.get_deals_appids()
        self.access_appids(appids_list)
        self.logger.info('Steam scraping done')