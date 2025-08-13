from airflow.providers.docker.operators.docker import DockerOperator
from airflow import DAG
from src.orchestrate.crawler.ps_tool import MyPlaystationCrawler
from src.orchestrate.crawler.xbox_tool import MyXboxCrawler
from src.orchestrate.crawler.steam_tool import MySteamCrawler
import datetime

@dag(
    start_date = datetime.datetime(2025, 8, 13, tz = 'UTC'),
    catchup = True,
    tag = ['scraper', 'crawler'],
    schedule = '@daily'
)
def playstation_dag():
    ps_crawler = MyPlaystationCrawler()
    