from src.orchestrate.crawler.ps_tool import MyPlaystationCrawler

if __name__ == "__main__":
    ps_crawler = MyPlaystationCrawler()
    ps_crawler.full_process()