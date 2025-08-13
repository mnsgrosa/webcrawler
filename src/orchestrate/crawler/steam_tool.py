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

class MySteamCrawler(MyCrawler):
    def __init__(self):
        super().__init__(__name__)
        self.platform = 'pc'
        self.current_url = 'https://store.steampowered.com/'
        self.base_url = self.current_url
        self.games_list = []

    @contextmanager
    def get_webdriver(self):
        driver = None
        try:
            self.logger.info('Creating steam driver')
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage") 
            driver = webdriver.Chrome(
                options=chrome_options
            )

            self.logger.info(f'Driver created and navigating to {self.current_url}')
            driver.get(self.current_url)
            yield driver

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
                        'date': date.isoformat(),
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
        self.logger.info('Starting the steam process')
        if self.current_url != self.base_url:
            self.logger.error(f'Returning to the base url located @ {self.current_url}')
            self.current_url = self.base_url
            return []
        
        self.get_deals_page()
        appids_list = self.get_deals_appids()
        self.access_appids(appids_list)
        self.post_contents()
        self.logger.info('Steam scraping done')