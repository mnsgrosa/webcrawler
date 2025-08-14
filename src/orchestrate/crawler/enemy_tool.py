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

class TheEnemyCrawler(MyCrawler):
    def __init__(self):
        super().__init__(__name__)
        self.platform = 'TheEnemy'
        self.base_url = 'https://www.theenemy.com.br/news'
        self.url = self.base_url
        self.news_list = []

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

    def get_news_links(self):
        try:
            soup = BeautifulSoup(self.url, 'html.parser')
            articles = soup.find_all('article', class_ = 'news-list__item')
            self.logger.info(f'Found {len(articles)} articles')
            for article in articles:
                title_tag = article.find('a', class_='news-list__item__content__title')
                title = title_tage.get_text(strip = True) if title_tag else 'Sem titulo'
                self.logger.info(f'Title: {title}')

                description_tag = article.find('p', class_='news-list__item__content__description')
                description = description_tag.get_text(strip = True) if description_tag else 'Sem descricao'
                self.logger.info(f'Description: {description}')

                relative_link = title_tag['href'] if title_tag else ''
                full_link = self.base_url + relative_link
                self.logger.info(f'Link: {full_link}')

                time_tag = article.find('div', class_='news-list__item__content__info__time').find('span')
                pub_time = time_tag.get_text(strip=True) if time_tag else "Sem data de publicacao"
                self.logger.info(f'Published time: {pub_time}')

                new_soup = BeautifulSoup(full_link, 'html.parser')
                author_grid = new_soup.find('span', class_ = 'content-title_info__author')
                self.logger.info(f'Entering: {full_link}')
                if author_grid:
                    author_tag = author_grid.find('a')
                    author = author_tag.get_text(strip = True) if author_tag else 'desconhecido'
                    self.logger.info(f'Author: {author}')
                else:
                    author_name = 'secao de autor ausente'
                    self.logger.info(f'No author found')

                main_content = new_soup.find('div', class_ = 'main-content_wrapper')
                paragraphs = main_content.find_all('p')

                full_text = '\n'.join(p.get_text(strip = True) for p in paragraphs)
                self.logger.info(f'Full text: {full_text}')

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