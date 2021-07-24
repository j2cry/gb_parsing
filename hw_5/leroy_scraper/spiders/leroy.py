import scrapy
from scrapy.http import HtmlResponse
from hw_5.leroy_scraper.items import LeroyScraperItem
from scrapy.loader import ItemLoader


class LeroyScraperSpider(scrapy.Spider):
    # user params

    # scrapper settings
    name = 'leroy_scraper'
    allowed_domains = ['leroymerlin.ru']
    start_urls = [f'https://leroymerlin.ru/catalogue/elektricheskie-vodonagrevateli-nakopitelnye/']

    def parse(self, response: HtmlResponse):
        # parsing next page url
        next_page = response.xpath('//a[contains(@class, "s15wh9uj_plp")][last()]/@href').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        # get links on current page
        links = response.xpath('//a[contains(@class, "iypgduq_plp")]/@href').extract()
        for link in links:
            yield response.follow(link, callback=self.product_parse)

    def product_parse(self, response: HtmlResponse):
        # get product characteristics
        _id = response.xpath('//span[@slot="article"]/@content').get('')
        title = response.xpath('//h1[@slot="title"]/text()').get('')
        link = response.url
        images = response.xpath('//picture[@slot="pictures"]/source[1]/@srcset').extract()
        yield LeroyScraperItem(_id=_id,
                               title=title,
                               link=link,
                               images=images)

    def features_parse(self, response: HtmlResponse):
        features = ItemLoader(item=LeroyScraperItem(), response=response)
        features.add_xpath('price', '')

        return features.load_item()
