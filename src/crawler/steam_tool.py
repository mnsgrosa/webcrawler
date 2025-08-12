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
        self.platform = 'steam'
        self.url = 'https://store.steampowered.com/'
        self.firefox_options = Options()
        self.firefox_options.add_argument("--headless")
        self.games_list = []

    @contextmanager
    def get_webdriver(self):
        driver = None
        try:
            if driver is None: 
                self.logger.info('Creating steam driver')
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

    def get_deals_url(self):
        if self.url != 'https://store.steampowered.com/':
            self.logger.info('Steam page not located at base page')
            return None
        
        with self.get_webdriver() as driver:
            try:
                self.logger.info('Starting to get steam deal page')
                wait = WebDriverWait(driver, 5)
                specials_button = wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'Specials')))
                self.logger.info('Element loaded')
                specials_button.click()
                self.url = driver.current_url
                self.logger.info('Redirected to deals page')
                return self.url
            except Exception as e:
                self.logger.error(f'Couldnt get to deals page: {e}')
                return None
    
    def get_deals_appids(self):
        if self.url == 'https://store.steampowered.com/':
            self.logger.info('Deals page not initialized')
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
        except Exception as e:
            self.logger.error(f'Couldnt get appids: {e}')
            return []