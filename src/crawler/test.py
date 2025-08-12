from tool import MyCrawler

if __name__ == '__main__':
    crawler = MyCrawler()
    crawler.get_all_deals_page()
    crawler.get_contents()