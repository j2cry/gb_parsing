import requests
import re
import pandas as pd
from fake_headers import Headers
from bs4 import BeautifulSoup as bs


URL_HH = 'https://hh.ru/search/vacancy'
URL_SJ = 'https://www.superjob.ru/'
df_cols = ['Title', 'Salary (min)', 'Salary (max)', 'Currency', 'Link', 'Source']
vacancy = 'Data scientist'
pages = 3

# vacancies = {'title': str,
#              'min_salary': float,
#              'max_salary': float,
#              'link': str,
#              'source': str}


def parse_hh_page(pg_num: int, **kwargs):
    hdr = kwargs.get('header', Headers(headers=True).generate())
    vcn = kwargs.get('vacancy', '')
    vacancy_param = {'text': vcn, 'page': pg_num}

    # request to HeadHunter
    response = requests.get(URL_HH, params=vacancy_param, headers=hdr)
    # parsing
    soup = bs(response.text, 'lxml')

    vacancy_headers = [elem for elem in soup.find_all(class_='vacancy-serp-item__row_header')]
    titles = [elem.find(class_='resume-search-item__name').text for elem in vacancy_headers]
    links = [url.get('href') for elem in vacancy_headers for url in elem('a')]
    salaries = [salary.text.replace('\u202f', '') if (salary := elem.find(class_='vacancy-serp-item__sidebar')) else ''
                for elem in vacancy_headers]
    currencies = [spl[-1] if (spl := cur.split()) else '' for cur in salaries]

    # parse salaries: min/max
    min_salaries, max_salaries = [], []
    for sal in salaries:
        regex = re.findall(r'(\d+)', sal)
        if len(regex) > 1:
            min_salaries.append(regex[0])
            max_salaries.append(regex[1])
        elif len(regex) > 0:
            if sal.find(u'от') != -1:
                min_salaries.append(regex[0])
                max_salaries.append('')
            else:
                min_salaries.append('')
                max_salaries.append(regex[0])
        else:
            min_salaries.append('')
            max_salaries.append('')

    return pd.DataFrame([titles, min_salaries, max_salaries, currencies, links, ['https://hh.ru/'] * len(titles)],
                        index=df_cols).T


def parse_sj_page(pg_num: int, **kwargs):
    hdr = kwargs.get('header', Headers(headers=True).generate())
    vcn = kwargs.get('vacancy', '')
    vacancy_param = {'text': vcn, 'page': pg_num}

    # request to SuperJob
    # response = requests.get(URL_SJ, params=vacancy_param, headers=hdr)
    # parsing
    # soup = bs(response.text, 'lxml')


if __name__ == '__main__':
    header = Headers(headers=True).generate()
    df = pd.DataFrame(columns=df_cols)
    for pg in range(pages):
        df = df.append(parse_hh_page(pg, header=header, vacancy=vacancy), ignore_index=True)

    df.index = df.index + 1
    df.to_csv('vacancies.csv')

