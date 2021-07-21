import requests
from lxml import html
from collections import defaultdict
from fake_headers import Headers
from time import sleep
from random import randint

# запилить запрос в декоратор - чисто ради тренировки
# перенести XPath запросы в словарь: 'newsmail': 'блаблабла', 'lenta': 'блеблебле' - но это скорее всего анрил


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
    # Яндекс блокирует автоматические запросы, поэтому сделать как для предыдущих источников пока не выходит
    # я честно попытался повоевать с их капчей, но
    header = Headers().generate()
    response = requests.get('https://yandex.ru/news/', headers=header)
    root = html.fromstring(response.text)

    titles = root.xpath('//div[contains(@class, "news-top-flexible-stories")]//h2[@class="mg-card__title"]/text()')
    links = root.xpath('//div[contains(@class, "news-top-flexible-stories")]//a[@class="mg-card__link"]/@href')
    links = [ln[:ln.find('?')] for ln in links]
    published_at = root.xpath('//div[contains(@class, "news-top-flexible-stories")]//span[@class="mg-card-source__time"]/text()')
    sources = root.xpath('//div[contains(@class, "news-top-flexible-stories")]//a[@class="mg-card__source-link"]/text()')

    day_news = [{'link': links[i],
                 'title': titles[i].replace('\xa0', ' '),
                 'published_at': published_at[i],
                 'source': sources[i]} for i in range(len(titles))]

    return day_news


# def test():
#     session = requests.Session()
#     header = {
#         'Host': 'yandex.ru',
#         'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0',
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#         'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
#         'Accept-Encoding': 'gzip, deflate, br',
#         # 'Referer': 'https://yandex.ru/news/',
#         'Connection': 'keep-alive',
#         # Cookie: news_lang=ru; nc=tips=1626885349507%3Bfavorites-button:1; yandexuid=1142951861626885334; is_gdpr=0; is_gdpr_b=CPT0GBCbOygC; yp=1629477334.ygu.1#1642653338.szm.1:1920x1080:1280x725#1629563749.csc.1; mda=0; yandex_gid=213; _yasc=JHL3ERjKcmebWwjUYOSVRAi4KXiBf9dP4lvLZuh7SfpbOFBXk/GLm9JovsA=; i=M8eknlWjLy+JhvcHvnYg2ApEiP770MGXX7eJ54OxPIPWN65xGb7XfnEr1GM4nisa4Ptp5mOV7L1HJhyHDm324mqiL70=; font_loaded=YSv1; ymex=1942245335.yrts.1626885335; yabs-frequency=/5/0000000000000000/dFzoS9G0003iGI62OK5jXW000En18m00/; gdpr=0; _ym_uid=1626885335255600019; _ym_d=1626885336; my=YwA=; _ym_isad=2; spravka=dD0xNjI2ODg1MzQ4O2k9MmEwMDoxMzcwOjgxMGM6NmYyOTpmYzFmOjZlY2E6NmM2NTo3OTYwO0Q9QzA0Mjg0MjJBNUJCQkEwMDE0REQ2Q0UzRUI3M0NCM0Q4NjhCREI5RTMyRjRFOTFFNDdERDA5RTVFMUFEOTI2Rjt1PTE2MjY4ODUzNDg0MzA3NzU5MDc7aD0yOTg0MGNhYmVmYTBlZDJiNzdlZDcwODVjYWU3OTA1MQ==; cycada=FgAF17IqOzDIa9eaowHQ3tS3jzuZ0N8bx/HdeIZPces=
#         'Upgrade-Insecure-Requests': '1',
#         'Sec-Fetch-Dest': 'document',
#         'Sec-Fetch-Mode': 'navigate',
#         'Sec-Fetch-Site': 'none',
#         'Sec-Fetch-User': '?1',
#         # 'Cache-Control': 'max-age=0',
#         'TE': 'trailers',
#     }
#     session.headers = header
#     response = session.get('https://yandex.ru/news/')
#     root = html.fromstring(response.text)
#
#     # get links to day news
#     links = root.xpath('//div[contains(@class, "news-top-flexible-stories")]//a[@class="mg-card__link"]/@href')
#     # links = [ln[:ln.find('?')] for ln in links]
#
#     session.headers.update({'Referer': 'https://yandex.ru/news/',
#                             'Sec-Fetch-Site': 'same-origin',
#                             'Cache-Control': 'max-age=0'})
#     for link in links:
#         # sleep(5)
#         response = session.get(link)
#         print(response.url)
#         print(response.text)

#         root = html.fromstring(response.text)
#         link = root.xpath('//a[@class="news-story__subtitle"]/@href')
#         print(link)


if __name__ == '__main__':
    sources = ['https://news.mail.ru/', 'https://lenta.ru/']
    news = [item for source in sources for item in get_news(source)]
    news.extend(get_yandex_news())
    print(*news, sep='\n')
    # get_yandex_news()
    # test()
