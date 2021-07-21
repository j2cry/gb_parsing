import requests
from lxml import html
from collections import defaultdict
from fake_headers import Headers
from time import sleep

# запилить запрос в декоратор - чисто ради тренировки
# перенести XPath запросы в словарь: 'newsmail': 'блаблабла', 'lenta': 'блеблебле' - но это скорее всего анрил


rules = {
    'https://news.mail.ru/': {'links': '//div[contains(@class, "daynews__item")]/a/@href',
                              'title': '//h1[@class="hdr__inner"]/text()',
                              'published_at': '//span[contains(@class, "note__text")]/@datetime',
                              'source': '//a[contains(@class, "breadcrumbs__link")]/@href'},

    'https://lenta.ru/': {'links': '//div[@class="b-yellow-box__wrap"]/div/a/@href',
                          'title': '//h1[@class="b-topic__title"]/text()',
                          'published_at': '//time[@class="g-date"]/@datetime',
                          'source': '$a=url'},

    # 'https://yandex.ru/news/': {'links': '//div[contains(@class, "news-top-flexible-stories")]//a[@class="mg-card__link"]/@href',
    #                             },
    # 'https://yandex.ru/news/': {'links': '//div[contains(@class, "news-top-flexible-stories")]/div/article/div[@class="mg-card__text-content"]/div/a/@href',
    #                             },

    # 'new_source': {'links': '',
    #                '': ''},
}


def get_news(url):
    if not (parse_rules := rules.get(url)):
        exit(f'Cannot find parse rules for given URL: {url}!')
    header = Headers().generate()
    response = requests.get(url, headers=header)
    root = html.fromstring(response.text)

    # get links to day news
    if not (links_rule := parse_rules.get('links')):
        exit(f'Cannot find `links` rule for given source: {url}!')
    links = root.xpath(links_rule)
    # iterate through day news collection and collect info
    day_news = []
    for link in links:
        news_item = defaultdict(str)
        news_item['link'] = link if link.startswith(url) else url + link[1:]

        response = requests.get(news_item['link'], headers=header)
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
    # session = requests.Session()
    header = Headers(headers=True).generate()
    response = requests.get('https://yandex.ru/news/', headers=header)

    root = html.fromstring(response.text)

    # get links to day news
    links = root.xpath('//div[contains(@class, "news-top-flexible-stories")]//a[@class="mg-card__link"]/@href')
    # mg-card__source-link
    print(links)

    for link in links:
        print(link)     # link[:link.find('--')
        response = requests.get(link, headers=header)
        root = html.fromstring(response.text)
        link = root.xpath('//a[@class="news-story__title-link"]/@href')[0]
        # link = root.xpath('//div[@class="news-story__head"]/a/@href')[0]       # почему блять ты не работаешь
        print(link)
        # get datetime
        # response = requests.get(link, headers=header)
        # root = html.fromstring(response.text)
        # published_at = root.xpath('time/@datetime')
        # print(published_at)
        sleep(2)


def test():
    header = Headers(headers=True).generate()
    url = 'https://yandex.ru/news/story/Zamnachalnika_Stavropolskogo_UGIBDD_Tkachenko_zaderzhan_vMoskve--f7ab8a8885e5dc387a4f577a40136fab?lang=ru&from=main_portal&fan=1&stid=-GrYgyJ3fWt69TF8gpja&t=1626867004&persistent_id=153721618&lr=213&msid=1626867380.30222.85684.195720&mlid=1626867004.glob_225.f7ab8a88&utm_source=morda_desktop&utm_medium=topnews_news'
    response = requests.get(url)
    root = html.fromstring(response.text)
    link = root.xpath('//a[@class="news-story__title-link"]/@href')
    print(link)


if __name__ == '__main__':
    # sources = ['https://news.mail.ru/', 'https://lenta.ru/', 'https://yandex.ru/news/']
    # news = [item for source in sources for item in get_news(source)]
    # print(*news, sep='\n')

    # get_yandex_news()
    test()
    # print(*get_yandex_news(), sep='\n')
