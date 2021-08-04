import os
import pathlib
import urllib.request
import zipfile

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
        """ Download dataset archive, unpack and prepare """
        ds_xpath = f'(//span[@id="dropDepartmentsLink"])[{ds_num if ds_num > 0 else 1}]'

        self.driver.get('https://data.mos.ru/opendata')
        try:
            data_element = self.driver.find_element_by_xpath(ds_xpath)
        except NoSuchElementException:
            return
        ActionChains(self.driver).move_to_element(data_element).perform()
        data_element.click()
        data_link, file_type = None, None
        # check available dataset formats
        for ft in self.file_types:
            try:
                data_link = self.driver.find_element_by_xpath(f'//ul[@id="dropExport"]//a[text()="{ft}"]')
                file_type = ft
                break
            except NoSuchElementException:
                pass
        if not data_link:       # no available types found
            return
        data_link = data_link.get_attribute('href')
        self.driver.close()

        cwd = pathlib.Path().cwd()
        tf_path = cwd.joinpath('tempfile')
        urllib.request.urlretrieve(data_link, tf_path)
        # unzip downloaded file
        with zipfile.ZipFile(tf_path, 'r') as zip_file:
            zip_file.extractall(cwd)
        tf_path.unlink()

        for filename in os.listdir(cwd):
            if filename.endswith(file_type):
                self.prepare(pathlib.Path(filename), file_type)

    @staticmethod
    def prepare(file_path, file_type):
        """ Drop NaN columns and save to .csv
            :param file_path: Path to file that contains open data
            :param file_type: File extension
        """
        ft_switcher = {'csv': lambda: pd.read_csv(file_path),
                       'xlsx': lambda: pd.read_excel(file_path)}
        if file_type not in ft_switcher.keys():
            return False
        df = ft_switcher[file_type]()
        df.dropna(axis=1, inplace=True)     # drop NaN columns
        df_path = pathlib.Path(file_path).name.replace(file_type, 'csv')
        df.to_csv(df_path)


if __name__ == '__main__':
    pre = MosOpenDataPreparer()
    pre.get(140)
