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

class VoxelCrawler(MyCrawler):
    def __init__(self):
        super().__init__(__name__)
        self.platform = 'voxel'
        self.base_url = 'https://www.tecmundo.com.br/voxel'
        self.current_url = self.base_url
        self.news_list = []

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

    def get_news_page(self):
        try:
            soup = BeautifulSoup(self.current_url, 'html.parser')
            news = soup.find_all('article')

            for new in news:
                link_tag = new.find('a')
                link = link_tag['href'] if link_tag else ''
                full_link = self.url + link
                self.logger.info(f'Link: {full_link}')                

                title_tag = new.find('h3')
                title = title_tag.get_text(strip = True) if title_tag else 'Sem titulo'
                description = title
                self.logger.info('Title: {title}')

                if full_link != self.current_url:
                    new_soup = BeautifulSoup(full_link, 'html.parser')
                    author_tag = new_soup.find('a', class_ = 'syles_author_name__XZAs0')
                    author = author_tag.get_text(strip = True) if author_tag else 'desconhecido'
                    self.logger.info(f'Author: {author}')

                    pub_tag = new_soup.find_all('p', class_ = 'flex items-center gap-1')
                    for tag in pub_tag:
                        text = tag.get_text(strip = True)
                        if 'Atualizado' not in text:
                            pub_time = text
                            self.logger.info(f'Published time: {pub_time}')

                    texts_tags = new_soup.find_all('p', class_ = 'MsoNormal')
                    full_text = '\n'.join(text.get_text(strip = True) for text in texts_tags)
                    self.logger.info(f'Full text: {full_text}')

                else:
                    author = 'secao de autor ausente'
                    pub_time = 'secao de data de publicacao ausente'
                    full_text = 'secao de texto ausente'

                self.news_list.append({
                    'title': title,
                    'description': description,
                    'link': full_link,
                    'pub_time': pub_time,
                    'author': author,
                    'full_text': full_text,
                    'platform': self.platform
                })
            self.logger.info('Got all news')
            return self.news_list
        except Exception as e:
            self.logger.error(f'Couldnt get news links: {e}', exc_info = True)
            return []

    def post_news(self):
        if self.news_list is None:
            self.logger.error(f'No news to post')
            return {}
        
        try:
            self.logger.info('Starting to post the news')
            with httpx.Client() as client:
                response = client.post('http://api:9000/post/news', json = {'items':self.news_list})
                response.raise_for_status()
            self.logger.info(f"News posted: {response.json().get('status')}")
            return response.json()
        except Exception as e:
            self.logger.error(f'Failed to post news: {e}')
            return {}