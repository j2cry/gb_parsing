# Написать приложение, которое собирает основные новости с сайтов mail.ru, lenta.ru, yandex-новости. Для парсинга
# использовать XPath. Структура данных должна содержать:
# название источника;
# наименование новости;
# ссылку на новость;
# дата публикации.

import requests
from lxml import html
from collections import defaultdict
from fake_headers import Headers
from time import sleep


rules = {
    'https://news.mail.ru/': {'links': '//div[contains(@class, "daynews__item")]/a/@href',
                              'title': '//div[contains(@class, "article")]//h1[@class="hdr__inner"]/text()',
                              'published_at': '//span[contains(@class, "note__text")]/@datetime',
                              'source': '//a[contains(@class, "breadcrumbs__link")]/@href'},

    'https://lenta.ru/': {'links': '//div[@class="b-yellow-box__wrap"]/div/a/@href',
                          'title': '//h1[@class="b-topic__title"]/text()',
                          'published_at': '//time[@class="g-date"]/@datetime',
                          'source': '$a=url'},

    # 'new_source': {'links': '',
    #                '': ''},
}


def get_news(url):
    if not (parse_rules := rules.get(url)):
        exit(f'Cannot find parse rules for given URL: {url}!')
    session = requests.Session()
    session.headers = Headers().generate()
    response = session.get(url)
    root = html.fromstring(response.text)

    # get links to day news
    if not (links_rule := parse_rules.get('links')):
        exit(f'Cannot find `links` rule for given source: {url}!')
    links = root.xpath(links_rule)
    # iterate through day news collection and collect info
    day_news = []
    for link in links:
        sleep(1)
        # drop links to third-party sites
        if (link.startswith('http') and not link.startswith(url)) or (link.find('/extlink/') != -1):
            continue
        news_item = defaultdict(str)
        news_item['link'] = link if link.startswith('http') else url + link[1:]

        response = session.get(news_item['link'])
        root = html.fromstring(response.text)
        for var, rule in parse_rules.items():
            if var == 'links':      # skip `links` rule
                pass
            elif rule.startswith('$c='):         # set constant to field
                news_item[var] = rule[3:]
            elif rule.startswith('$a='):         # set as named attr
                news_item[var] = locals().get(rule[3:], None)
            else:       # parse others
                value = root.xpath(rule)[0]
                news_item[var] = value if var != 'title' else value.replace('\xa0', ' ')
        day_news.append(news_item)
    return day_news


def get_yandex_news():
    # Яндекс блокирует автоматические запросы, поэтому сделать вывод как для предыдущих источников не выйдет
    # я честно попытался повоевать с их капчей, но безуспешно - там нужен серьезный подход :)
    header = Headers().generate()
    response = requests.get('https://yandex.ru/news/', headers=header)
    root = html.fromstring(response.text)

    titles = root.xpath('//div[contains(@class, "news-top-flexible-stories")]//h2[@class="mg-card__title"]/text()')
    links = root.xpath('//div[contains(@class, "news-top-flexible-stories")]//a[@class="mg-card__link"]/@href')
    links = [ln[:ln.find('?')] for ln in links]
    published_at = root.xpath('//div[contains(@class, "news-top-flexible-stories")]//'
                              'span[@class="mg-card-source__time"]/text()')
    sources = root.xpath('//div[contains(@class, "news-top-flexible-stories")]//'
                         'a[@class="mg-card__source-link"]/text()')

    day_news = [defaultdict(str, {'link': links[i],
                                  'title': titles[i].replace('\xa0', ' '),
                                  'published_at': published_at[i],
                                  'source': sources[i]}) for i in range(len(titles))]
    return day_news


if __name__ == '__main__':
    news_sources = ['https://news.mail.ru/', 'https://lenta.ru/']
    news = [item for source in news_sources for item in get_news(source)]
    news.extend(get_yandex_news())
    print(*news, sep='\n')
