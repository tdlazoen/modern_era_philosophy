import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import requests
from bs4 import BeautifulSoup
import time
import re
import sys
import os
sys.path.append(os.path.abspath('..'))
from modern_dfs import ModernPhilosophers, ModernDocuments

'''
This file scrapes the website
https://www.marxists.org/reference/subject/philosophy/
for modern era philosophical texts
'''

def init_driver():
    '''
    INPUT:
        None
    OUTPUT:
        driver - selenium Chrome web driver
    '''
    driver = webdriver.Chrome()
    driver.wait = WebDriverWait(driver, 5)

    return driver

def get_author_doc_info(phils, driver):
    '''
    INPUT:
        phils - modern philosopher dataframe
        driver - selenium Chrome web driver
    OUTPUT:
        authors - document authors
        years - years each document was written
        links - links to each document's text
        titles - document titles

    Get the basic document info
    '''
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
    links[titles.index('computing machinery and intelligence')] = 'http://www.abelard.org/turpap/turpap.php'
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
    '''
    INPUT:
        link - link to document text
        driver - selenium Chrome web driver
    OUTPUT:
        text - text obtained from link; empty if retrieval failed

    Get text for a specific link
    '''
    r = requests.get(link)
    soup = BeautifulSoup(r.content, 'html.parser')

    exceptions = ['https://www.marxists.org/archive/marx/works/1867-c1/ch01.htm#S1', \
                  'https://www.marxists.org/archive/marx/works/1867-c1/ch01.htm#S2', \
                  'https://www.marxists.org/subject/women/authors/millett-kate/theory.htm']

    multiple_links = ['https://www.marxists.org/reference/archive/feuerbach/works/future/index.htm', \
                      'https://www.marxists.org/reference/archive/spirkin/works/dialectical-materialism/index.html', \
                      'https://www.marxists.org/archive/vygotsky/works/words/index.htm', \
                      'https://www.marxists.org/reference/archive/marcuse/works/reason/index.htm', \
                      'https://www.marxists.org/archive/novack/works/history/index.htm', \
                      'https://www.marxists.org/archive/lektorsky/subject-object/index.htm']

    if link in multiple_links:
        driver.get(link)
        time.sleep(2)

        if link == 'https://www.marxists.org/archive/novack/works/history/index.htm':
            lnks = driver.find_elements_by_xpath('/html/body/p[contains(@class, "toc") or contains(@class, "tob")][position() > 1]/a')
            lnks.pop()
        elif link == 'https://www.marxists.org/archive/lektorsky/subject-object/index.htm':
            lnks = driver.find_elements_by_xpath('/html/body/p[@class="fst"]//a')
            lnks.pop(10)
        elif link == 'https://www.marxists.org/archive/vygotsky/works/words/index.htm':
            lnks = driver.find_elements_by_xpath('/html/body/p[position() < 2]/a')
        else:
            lnks = driver.find_elements_by_xpath('/html/body/p[@class="index"]/a')
            lnks = [link for link in lnks if 'glossary' not in link.get_attribute('href')]

        text = ''
        for i in range(len(lnks)):
            if link == 'https://www.marxists.org/archive/novack/works/history/index.htm':
                lnks = driver.find_elements_by_xpath('/html/body/p[contains(@class, "toc") or contains(@class, "tob")][position() > 1]/a')
                lnks.pop()
            elif link == 'https://www.marxists.org/archive/lektorsky/subject-object/index.htm':
                lnks = driver.find_elements_by_xpath('/html/body/p[@class="fst"]//a')
                lnks.pop(10)
            elif link == 'https://www.marxists.org/archive/vygotsky/works/words/index.htm':
                lnks = driver.find_elements_by_xpath('/html/body/p[@class="index"][position() < 2]/a')
            else:
                lnks = driver.find_elements_by_xpath('/html/body/p[@class="index"]/a')
                lnks = [link for link in lnks if 'glossary' not in link.get_attribute('href')]

            lnks[i].click()
            time.sleep(1)

            pars = driver.find_elements_by_tag_name('p')
            text += ' '.join(x.text.strip() for x in pars)

            driver.back()
            time.sleep(2)
        return text

    elif len(soup.findAll('p', {'class': 'index'})) == 0 or link in exceptions:
        pars = soup.select('p')
        text = ' '.join(x.text for x in pars)
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
    '''
    INPUT:
        authors - document authors
        years - years each document was written
        links - document links
        titles - document titles
        driver - selenium Chrome web driver
        docs - documents dataframe
    OUTPUT:
        None
    Add documents from the website
    '''
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
    phils.save_df()
    add_documents(authors, years, links, titles, driver, docs)
    driver.quit()
    docs.save_df()
