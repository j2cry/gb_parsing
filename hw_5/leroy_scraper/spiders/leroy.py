import scrapy
from scrapy.http import HtmlResponse
from hw_5.leroy_scraper.items import LeroyScraperItem
from itemloaders import ItemLoader, processors
# from scrapy.loader import ItemLoader


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

    @staticmethod
    def product_parse(response: HtmlResponse):
        product = ItemLoader(item=LeroyScraperItem(), selector=response)
        product.default_output_processor = processors.Join(' ')

        product.add_xpath('_id', '//span[@slot="article"]/@content')
        product.add_value('link', response.url)
        product.add_xpath('images', '//picture[@slot="pictures"]/source[1]/@srcset')
        product.add_xpath('title', '//h1[@slot="title"]/text()')
        product.add_xpath('price', '//span[@slot="price"]/text()')

        feature_keys = response.xpath('//dt[@class="def-list__term"]/text()').extract()
        feature_values = response.xpath('//dd[@class="def-list__definition"]/text()').extract()
        feature_values = [value.strip() for value in feature_values]
        features = list(zip(feature_keys, feature_values))
        product.add_value('features', features)

        # test = product.load_item()
        return product.load_item()
