import pathlib
import random
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient

# set your own path
DRIVER_PATH = pathlib.Path('chromedriver').absolute().as_posix()


def text_generator(words_amount: int):
    """ Generates collection of words """
    with open('words', 'r', encoding='utf-8') as f:
        words = []
        unique_words_amount = [n for n, _ in enumerate(f)][-1] + 1
        indexes = sorted([random.randint(0, unique_words_amount) for _ in range(words_amount)])
        f.seek(0, 0)
        for n, w in enumerate(f):
            while n in indexes:
                words.append(w.strip())
                indexes.remove(n)

    random.shuffle(words)
    return ' '.join(words)


# Chrome options
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')

# initialize driver
driver = webdriver.Chrome(DRIVER_PATH, options=chrome_options)
driver.get('https://tempmail.plus/en/#!')
driver.implicitly_wait(4)

# get mail params
domain = driver.find_element_by_id('domain').text
name = driver.find_element_by_id('pre_button').get_attribute('value')
address = name + domain

# send mail
for _ in range(random.randint(2, 6)):
    driver.find_element_by_id('compose').click()
    driver.find_element_by_id('to').send_keys(address)
    driver.find_element_by_id('subject').send_keys(text_generator(3))
    driver.find_element_by_id('text').send_keys(text_generator(random.randint(50, 150)))
    driver.find_element_by_id('submit').click()

# waiting for all messages to be received
sleep(10)

# collect inbox
mail_collection = []    # from, date, subject, text

# save unique params for each mail on page
inbox_onclick = [i.get_attribute('onclick') for i in driver.find_elements_by_xpath('//div[@class="mail"]')]

# iterate through emails and collect info
for onclick_id in inbox_onclick:
    sender = driver.find_element_by_xpath('//div[contains(@class, "from")]/span').text

    driver.find_element_by_xpath(f'//div[@onclick="{onclick_id}"]').click()
    subject = driver.find_element_by_xpath('//div[contains(@class, "subject")]').text
    date_time = driver.find_element_by_xpath('//span[contains(@class, "date")]').get_attribute('data-date')
    text = driver.find_element_by_xpath('//div[contains(@class, "overflow-auto")]').text
    driver.find_element_by_id('back').click()

    mail_collection.append({'sender': sender,
                            'subject': subject,
                            'datetime': date_time,
                            'text': text})

driver.close()

# push to DB
client = MongoClient('mongodb://localhost:27017/')
db = client['gb_homework']
collection = db['emails']
collection.insert_many(mail_collection)
