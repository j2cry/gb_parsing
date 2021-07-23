from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from hw_5.job_scraper import settings
from hw_5.job_scraper.spiders.job_scraper import JobScraperSpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(JobScraperSpider)
    # process.crawl(AnotherJobScraperSpider)
    process.start()
