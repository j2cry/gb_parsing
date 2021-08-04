import pathlib
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options

# set your own path
DRIVER_PATH = pathlib.Path('chromedriver').absolute().as_posix()


class MosOpenDataPreparer:
    def __init__(self, file_types=('csv', 'xlsx')):
        # Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--start-maximized')
        # initialize driver
        self.driver = webdriver.Chrome(DRIVER_PATH, options=chrome_options)
        self.driver.implicitly_wait(4)
        self.file_types = file_types

    def get(self, ds_num: int):
        # (//li[@itemscope="itemscope"])[...]/a/div/span[@class="dataset-number"]
        # (//span[@id="dropDepartmentsLink"])[140]
        ds_xpath = f'(//span[@id="dropDepartmentsLink"])[{ds_num if ds_num > 0 else 1}]'

        self.driver.get('https://data.mos.ru/opendata')
        try:
            data_element = self.driver.find_element_by_xpath(ds_xpath)
        except NoSuchElementException:
            return False
        ActionChains(self.driver).move_to_element(data_element).perform()
        data_element.click()
        data_link = None
        # check available types
        for file_type in self.file_types:
            try:
                data_link = self.driver.find_element_by_xpath(f'//ul[@id="dropExport"]//a[text()="{file_type}"]')
                break
            except NoSuchElementException:
                pass
        if not data_link:       # no available types found
            return False
        data_link = data_link.get_attribute('href')

        self.driver.get(data_link)

        # self.driver.close()

    def __prepare(self, df: pd.DataFrame):
        pass


if __name__ == '__main__':
    pre = MosOpenDataPreparer()
    pre.get(140)
