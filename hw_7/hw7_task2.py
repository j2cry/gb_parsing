import pathlib
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
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
                'products': '/div/ul/li',
                'attribute': 'rel'},    # [@rel="!$n"]
               # {}
               ]


def get_xpath(d: dict, key: str):
    """ Get value from dict, adding `block` """
    return d.get('block') + d.get(key)


# Chrome options
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
# initialize driver
driver = webdriver.Chrome(DRIVER_PATH, options=chrome_options)
driver.implicitly_wait(3)

for shop in SHOP_PARAMS:
    driver.get(shop.get('url'))
    driver.execute_script("window.scrollTo(0, 1080);")

    next_button = 1
    while next_button:
        next_button = driver.find_element_by_xpath(get_xpath(shop, 'next'))
        next_button.click()
        try:
            # try to determine if next-button is disabled
            driver.find_element_by_xpath(get_xpath(shop, 'next_disabled'))
            next_button = None
        except NoSuchElementException:
            pass
    # collect product unique attributes
    product_urls = [p.find_element_by_xpath('.//a').get_attribute('href')
                    for p in driver.find_elements_by_xpath(get_xpath(shop, 'products'))]

    products_collection = []
    for url in product_urls:
        # open product page
        driver.get(url)
        # parsing product info
        # blablabla
        # driver.back()

        products_collection.append({'key': 'value'})

    # push to db

driver.close()
