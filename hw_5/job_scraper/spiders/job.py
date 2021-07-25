import re
import scrapy
from itemloaders import ItemLoader, processors
from scrapy.http import HtmlResponse
from urllib.parse import urlparse
from hw_5.job_scraper.items import JobScraperItem


class JobScraperSpider(scrapy.Spider):
    # user params
    job_title = 'data'

    # parsing rules
    scrap_rules = {
        'hh.ru': {'next_page': '//a[@data-qa="pager-next"]/@href',
                  'vacancy_links': '//a[@data-qa="vacancy-serp__vacancy-title"]/@href',
                  'title': '//h1[@data-qa="vacancy-title"]//text()',
                  'salary': '//p[@class="vacancy-salary"]//text()[1]',
                  },

        'superjob.ru': {'next_page': '//a[contains(@class, "f-test-button-dalshe")]/@href',
                        'vacancy_links': '//a[contains(@class, "_6AfZ9")]/@href',
                        'title': '//h1[contains(@class, "_1h3Zg")]/text()',
                        'salary': '//div[contains(@class, "_3MVeX")]//span[contains(@class, "_2Wp8I")]/text()',
                        }
        }
    # scrapper settings
    name = 'job_scraper'
    allowed_domains = ['hh.ru', 'superjob.ru']
    # allowed_domains = ['hh.ru']           # если надо разделить на 2 паука
    # allowed_domains = ['superjob.ru']
    start_urls = [f'https://hh.ru/search/vacancy?text={job_title}',
                  f'https://www.superjob.ru/vacancy/search/?keywords={job_title}']
    # start_urls = [f'https://hh.ru/search/vacancy?text={job_title}']       # если надо разделить на 2 паука
    # start_urls = [f'https://www.superjob.ru/vacancy/search/?keywords={job_title}']
    rules = None

    def parse(self, response: HtmlResponse, **kwargs):
        # get parsing rules for current domain
        for domain in self.allowed_domains:
            if response.url.find(domain) > 0:
                self.rules = self.scrap_rules.get(domain, None)
                break

        # parsing next page url
        next_page = response.xpath(self.rules.get('next_page')).extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        # get links on current page
        links = response.xpath(self.rules.get('vacancy_links')).extract()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        vacancy = ItemLoader(item=JobScraperItem(), selector=response)
        vacancy.default_output_processor = processors.Join(' ')
        vacancy.add_xpath('title', self.rules.get('title'))
        link = response.url[:index] if (index := response.url.find('?')) != -1 else response.url
        vacancy.add_value('link', link)
        parsed_link = urlparse(link)
        vacancy.add_value('source', f'{parsed_link.scheme}://{parsed_link.netloc}/')

        # parse salary and currency
        salary = ' '.join(response.xpath(self.rules.get('salary')).getall())
        salary = salary.replace('\xa0', '') if salary else ''
        regex = re.findall(r'(\d+)', salary)
        salary_switcher = {0: lambda: ('', ''),
                           1: lambda: (regex[0], '') if salary.find(u'от') > -1 else ('', regex[0]),
                           2: lambda: (regex[0], regex[1])}
        min_salary, max_salary = salary_switcher[len(regex)]()
        currency = spl[-1] if (spl := salary.split()) and (len(regex) > 0) else ''

        vacancy.add_value('min_salary', min_salary)
        vacancy.add_value('max_salary', max_salary)
        vacancy.add_value('currency', currency)

        yield vacancy.load_item()
