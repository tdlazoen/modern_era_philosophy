import pandas as pd
import numpy as np
from modern_dfs import ModernPhilosophers, ModernDocuments
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import requests
from bs4 import BeautifulSoup
import time
import re

def init_driver():
    driver = webdriver.Chrome()
    driver.wait = WebDriverWait(driver, 5)

    return driver

def get_author_doc_info(phils, driver):
    url = 'https://www.marxists.org/reference/subject/philosophy/'

    driver.get(url)
    time.sleep(2)
    titles = driver.find_elements_by_xpath('//p[@class = "item"]/a')
    titles = [x.text.lower().strip() for x in titles]
    titles = [x.replace('&', 'and') for x in titles]

    links = driver.find_elements_by_xpath('//p[@class = "item"]/a')
    links = [x.get_attribute('href').strip() for x in links]

    authors_years = driver.find_elements_by_css_selector('p.item')
    authors_string = '\n'.join(x.text for x in authors_years).lower()

    for title in titles:
        authors_string = authors_string.replace(title, '')

    idx1 = titles.index('de cive')
    idx2 = titles.index('origin of inequality')

    authors_years = authors_string.split('\n')
    authors_years.insert(idx1, ', thomas hobbes, 1650')
    authors_years.insert(idx2, ', jean-jacques rousseau, 1762')
    authors_years[links.index('https://www.marxists.org/archive/marx/works/1880/soc-utop/ch03.htm')] = ', frederick engels, 1877'
    authors_years[titles.index('the german ideology')] = ', karl marx, 1845'
    authors_years[titles.index('ludwig feuerbach, the end of classical german philosophy')] = ', frederick engels, 1888'

    idx_humboldt = titles.index('wilhelm von humboldt on language')
    idx_goethe = titles.index('goethe on science')
    titles[idx_humboldt] = 'on language'
    titles[idx_goethe] = 'on science'
    titles[titles.index('commodities: use value and value')] = 'commodities'
    authors_years[idx_humboldt] = ', wilhelm von humboldt, 1810'
    authors_years[idx_goethe] = ', johann wolfgang von goethe, 1798'

    idx_drop = [titles.index('history of philosophy'),\
                titles.index('classical german philosophy'), \
                titles.index('engels on hegel and schelling'), \
                titles.index('commodities: the two-fold character of labour'), \
                titles.index('the fetishism of commodities'), \
                titles.index("schelling's criticism of hegel"), \
                titles.index('on the significance of militant materialism')]

    for i, idx in enumerate(idx_drop):
        for lst in [titles, links, authors_years]:
            lst.pop(idx - i)

    authors = [re.split('\,', x)[1].lower().strip() for x in authors_years]
    years = [int(re.split('\,', x)[2][:5].lower().strip()) for x in authors_years]

    multiple_auth_idx = []
    for author in authors:
        if '&' in author:
            multiple_auth_idx.append(authors.index(author))

    for i, idx in enumerate(multiple_auth_idx):
        for lst in [titles, links, authors, years]:
            lst.pop(idx - i)

    for i in range(len(authors)):
        if authors[i] == 'g w f hegel':
            authors[i] = 'g.w.f. hegel'
        elif authors[i] == 'gottfried leibnitz':
            authors[i] = 'leibniz'
        elif authors[i] == 'benedicto spinoza':
            authors[i] = 'baruch spinoza'
        elif authors[i] == 'galilei galileo':
            authors[i] = ' '.join(x for x in authors[i].split()[::-1])
        elif authors[i] == 'alfred schuetz':
            authors[i] = 'alfred schutz'
        for philosopher in phils.df.name.values:
            if (authors[i] in philosopher) or (philosopher in authors[i]):
                authors[i] = philosopher
        # if authors[i] not in phils.df.name.values:
        #     phils.add_philosopher_entry(authors[i])

    return authors, years, links, titles

def get_text(link, driver):
    r = requests.get(link)
    soup = BeautifulSoup(r.content, 'html.parser')

    exceptions = ['https://www.marxists.org/archive/marx/works/1867-c1/ch01.htm#S1', \
                  'https://www.marxists.org/archive/marx/works/1867-c1/ch01.htm#S2']

    if len(soup.findAll('p', {'class': 'index'})) == 0 or link in exceptions:
        pars = soup.select('p')
        text = ' '.join(x.text for x in pars)
        return text
    elif link == 'https://www.marxists.org/reference/archive/feuerbach/works/future/index.htm':
        driver.get(link)
        time.sleep(2)

        lnks = driver.find_elements_by_xpath('/html/body/p[@class="index"]/a')
        lnks = [link for link in lnks if 'glossary' not in link.get_attribute('href')]

        text = ''
        for i in range(len(lnks)):
            lnks = driver.find_elements_by_xpath('/html/body/p[@class="index"]/a')
            lnks = [link for link in lnks if 'glossary' not in link.get_attribute('href')]
            lnks = [link for link in lnks if 'reference' not in link.get_attribute('href')]

            lnks[i].click()
            time.sleep(1)

            pars = driver.find_elements_by_tag_name('p')
            text += ' '.join(x.text.strip() for x in pars)

            driver.back()
            time.sleep(2)
        return text
    else:
        try:
            driver.get(link)
            time.sleep(2)

            link = driver.find_element_by_xpath('/html/body/p[@class="index"]/a')

            link.click()
            time.sleep(1)

            pars = driver.find_elements_by_tag_name('p')
            text = ' '.join(x.text.strip() for x in pars)

            return text
        except NoSuchElementException:
            return ''

def add_documents(authors, years, links, titles, driver, docs):
    for i in range(len(authors)):
        author = authors[i]
        year = years[i]
        link = links[i]
        title = titles[i]

        if title == 'discourse on method':
            continue

        print("\nGetting text for {} by {}".format(title, author))
        text = get_text(link, driver)
        print(len(text.split()))

        if text:
            print('Adding Document')
            docs.add_document(author, title, year, text, link)
        else:
            continue

if __name__ == '__main__':
    phils, docs = ModernPhilosophers(), ModernDocuments()
    driver = init_driver()
    authors, years, links, titles = get_author_doc_info(phils, driver)
    add_documents(authors, years, links, titles, driver, docs)
    driver.quit()
