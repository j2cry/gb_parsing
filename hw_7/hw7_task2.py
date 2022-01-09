# Написать программу, которая собирает «Хиты продаж» с сайтов техники М.видео, ОНЛАЙН ТРЕЙД и складывает данные в БД.
# Магазины можно выбрать свои. Главный критерий выбора: динамически загружаемые товары.

import pathlib
from collections import defaultdict

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient

# set your own path
DRIVER_PATH = pathlib.Path('chromedriver').absolute().as_posix()
# set shop site parameters
SHOP_PARAMS = [{'name': 'mvideo_hits',
                'url': 'https://www.mvideo.ru/',
                'block': '(//div[@class="accessories-carousel-wrapper "])[1]',
                'next': '/a[contains(@class, "right")]',
                'next_disabled': '/a[contains(@class, "right disabled")]',
                'products': '/div/ul/li//h3/a',
                'params_link': '//div[contains(@class, "o-pdp-about-product-specification__inner-block")]/a',
                'product_title': '//h1[@class="fl-h1"]',
                'product_price': '//div[@class="fl-pdp-price__current"]',
                'product_keys': '(//span[@class="product-details-overview-specification"])[position() mod 2 = 1]',
                'product_values': '(//span[@class="product-details-overview-specification"])[position() mod 2 = 0]'},

               # мне показалось, или хиты продаж на онлайнтрейде подгружаются все сразу, а не динамически?
               {'name': 'onlinetrade_hits',
                'url': 'https://www.onlinetrade.ru/',
                'block': '//div[@id="tabs_hits"]',
                'next': '/div[1]/span[2]',
                'next_disabled': '/div[1]/span[2][@aria-disabled="true"]',
                'products': '/div[2]//div[contains(@class, "indexGoods__item__flexCover")]/a',
                'params_link': '//div[contains(@class, "productPage__shortProperties")]/a',
                'product_title': '//h1[@itemprop="name"]',
                'product_price': '//span[@class="js__actualPrice"]',        # //span[@itemprop="price"] - без рубля
                'product_keys': '//ul[@class="featureList js__backlightingClick"]/li/span',
                'product_values': '//ul[@class="featureList js__backlightingClick"]/li'},
               ]


def get_xpath(d: dict, key: str):
    """ Get value from dict, adding `block` """
    return d.get('block') + d.get(key)


# Chrome options
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--start-maximized')
# initialize driver
driver = webdriver.Chrome(DRIVER_PATH, options=chrome_options)
driver.implicitly_wait(3)

for shop in SHOP_PARAMS:
    driver.get(shop.get('url'))
    driver.execute_script("window.scrollTo(0, 800);")

    next_button = 1
    while next_button:
        next_button = driver.find_element_by_xpath(get_xpath(shop, 'next'))
        try:
            next_button.click()
        except ElementClickInterceptedException:
            # если элемент не кликабельный в момент клика - уже (вроде) не актуально
            driver.execute_script("arguments[0].click();", next_button)

        # try to determine if next-button is disabled
        try:
            driver.find_element_by_xpath(get_xpath(shop, 'next_disabled'))
            next_button = None
        except NoSuchElementException:
            pass
    # collect product unique attributes
    product_urls = [p.get_attribute('href')
                    for p in driver.find_elements_by_xpath(get_xpath(shop, 'products'))]

    products_collection = []
    for url in product_urls:
        product_info = defaultdict(str)
        # open product page
        driver.get(url)
        # parse product info
        product_info['title'] = driver.find_element_by_xpath(shop.get('product_title')).text
        # намеренно не стал удалять символ рубля в конце - его тоже при необходимости можно парсить,
        # если вдруг цены не только в рублях
        product_info['price'] = driver.find_element_by_xpath(shop.get('product_price')).text.replace(' ', '')
        product_info['link'] = url

        # open product parameters page if required
        if params_link := shop.get('params_link', None):
            try:
                driver.find_element_by_xpath(params_link).click()
            except NoSuchElementException:
                # parameters not found
                break

            # collect product params
            keys = [k.text for k in driver.find_elements_by_xpath(shop.get('product_keys'))]
            values = [k.text.replace(keys[n], '')
                      for n, k in enumerate(driver.find_elements_by_xpath(shop.get('product_values')))]
            for k, v in zip(keys, values):
                product_info[k] = v

        products_collection.append(product_info)

    # push to db
    client = MongoClient('mongodb://localhost:27017/')
    db = client['gb_homework']
    collection = db[shop.get('name')]
    collection.insert_many(products_collection)

driver.close()
