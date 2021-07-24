from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from hw_5.leroy_scraper import settings
from hw_5.leroy_scraper.spiders.leroy import LeroyScraperSpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroyScraperSpider)
    process.start()
