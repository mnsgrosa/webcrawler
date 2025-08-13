from src.orchestrate.crawler.steam_tool import MySteamCrawler

if __name__ == "__main__":
    steam_crawler = MySteamCrawler()
    steam_crawler.full_process()