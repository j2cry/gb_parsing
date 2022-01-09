# В ранее написанное приложение добавить класс с функциями, которые позволят собрать открытые данные по выбранной
# теме при помощи Python с сайта (выберите из списка известных источников данных).

import enum
import os
import pathlib
import typing
import urllib.request
import zipfile

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options

# set your own path
DRIVER_PATH = pathlib.Path('chromedriver').absolute().as_posix()


class DataSelector(enum.Enum):
    DATASET = 1
    CATEGORY = 2

    @staticmethod
    def interpret(mode, num):
        """ Return xpath for selected dataset or category
            :param mode: DataSelector value
            :param num: Number of required dataset or category """
        interpreter = {DataSelector.DATASET: lambda: f'(//span[@id="dropDepartmentsLink"])[{num}]',
                       DataSelector.CATEGORY:
                           lambda: f'//ul[contains(@class, "category-{num}-list")]//span[@id="dropDepartmentsLink"]'}
        return interpreter.get(mode)()


class FormatProcessor(enum.Enum):
    """ Class for opening file as DataFrame according to its format """
    XLSX = '.xlsx'
    CSV = '.csv'

    @classmethod
    def supported(cls):
        """ Returns supported formats """
        return [getattr(FormatProcessor, f).value
                for f in cls.__dict__.keys() if (f[0] != '_') and (not callable(getattr(FormatProcessor, f)))]

    @classmethod
    def make(cls, filename):
        """ Returns opened file as DataFrame """
        # implement format here
        # иногда может всплывать UnicodeDecodeError, если в датасете есть какая-то дичь
        processor = {FormatProcessor.CSV.value: lambda path: pd.read_csv(path),
                     FormatProcessor.XLSX.value: lambda path: pd.read_excel(path)}
        # check for format implementation
        for ext in cls.supported():
            if ext not in processor.keys():
                raise ValueError(f'Processing for `{ext}` format not implemented!')
        filename = pathlib.Path(filename)
        # check for format support
        if filename.suffix not in processor.keys():
            raise ValueError(f'Unsupported format `{filename.suffix}`!')
        return processor.get(filename.suffix)(filename)


class MosOpenDataPreparer:
    """ Class for receiving open data from Moscow City Government """
    def __init__(self, file_types=('csv', 'xlsx'), target_folder='data'):
        self.url = 'https://data.mos.ru/opendata'
        self.link_xpath = f'//ul[@id="dropExport"]//a[text()="!$FT"]'
        # Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--start-maximized')
        # initialize driver
        self.driver = webdriver.Chrome(DRIVER_PATH, options=chrome_options)
        self.driver.implicitly_wait(4)
        self.file_types = file_types
        self.target_folder = pathlib.Path(target_folder).absolute()
        if not self.target_folder.exists():
            self.target_folder.mkdir()

    def __del__(self):
        self.driver.close()

    def __get_links(self, xpath: str):
        """ Get download links for datasets by xpath """
        self.driver.get(self.url)
        try:
            data_elements = self.driver.find_elements_by_xpath(xpath)
        except NoSuchElementException:
            print(f'No elements on `{xpath}` found.')
            return
        actions = ActionChains(self.driver)
        # iterate through found elements in category
        data_links = []
        for elem in data_elements:
            actions.move_to_element(elem).perform()
            elem.click()

            # check available dataset formats
            data_link = None
            for ft in self.file_types:
                try:
                    data_link = self.driver.find_element_by_xpath(self.link_xpath.replace('!$FT', ft))
                    break
                except NoSuchElementException:
                    pass
            if not data_link:       # no available types found
                continue
            data_links.append(data_link.get_attribute('href'))
        return data_links

    def __download(self, links: typing.List[str]):
        """ Download datasets from links """
        temp_file = self.target_folder.joinpath('temporary')
        for link in links:
            # download
            urllib.request.urlretrieve(link, temp_file)
            # unzip downloaded file
            with zipfile.ZipFile(temp_file, 'r') as zip_file:
                zip_file.extractall(self.target_folder)
        temp_file.unlink()

    @staticmethod
    def prepare(folder):
        """ Drop NaN columns and save datasets to .csv """
        for filename in os.listdir(folder):
            if (file_ext := pathlib.Path(filename).suffix) not in FormatProcessor.supported():
                print(f'No format processor found for file `{filename}`!')
                continue
            filename = pathlib.Path(folder).joinpath(filename)
            df = FormatProcessor.make(filename)
            df.dropna(axis=1, inplace=True)     # drop NaN columns
            filename = pathlib.Path(folder).joinpath(filename.name.replace(file_ext, '.csv'))
            df.to_csv(filename, encoding='utf-8')

    def get(self, mode: DataSelector, num: int):
        """ Download dataset archive, unpack and prepare """
        num = num if num > 0 else 1
        data_xpath = DataSelector.interpret(mode, num)
        links = self.__get_links(data_xpath)
        self.__download(links)
        self.prepare(self.target_folder)


if __name__ == '__main__':
    pre = MosOpenDataPreparer()
    pre.get(DataSelector.DATASET, 140)
    pre.get(DataSelector.CATEGORY, 15)
