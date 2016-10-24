from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import re
import os
from string import punctuation
from dataframes import Philosophers, Documents
from unidecode import unidecode

'''
This file was intended to scrape the site openculture
http://www.openculture.com/free-philosophy-ebooks
The scraping of the site wasn't performed as there wouldn't be enough data obtained for the amount of work needed.
'''

def init_driver():
    '''
    Initialize Selenium Driver
    '''
    driver = webdriver.Chrome()
    driver.wait = WebDriverWait(driver, 5)

    return driver

def get_initial_info(driver, phils):
    '''
    Exploratory web scraping - Getting basic information that would be needed to scrape documents
    '''
    url = 'http://www.openculture.com/free-philosophy-ebooks'
    driver.get(url)

    authors = driver.find_elements_by_xpath('//*[@id="contentmiddle"]/div/div/ul/li/strong')
    authors = [x.text.lower().strip(punctuation).strip() for x in authors][:-2]
    titles_links = driver.find_elements_by_xpath('//*[@id="contentmiddle"]/div/div/ul/li')
    titles = [x.text.lower().strip(punctuation).strip().split('\n')[0] for x in titles_links][:-2]
    idx = titles.index('')
    titles.pop(idx)

    links = driver.find_elements_by_xpath('//*[@id="contentmiddle"]/div/div/ul/li/ul/li/a')
    links = [x.get_attribute('href') for x in links if 'Read Online Now' in x.text][:-2]

    eastern_idxs = []
    prev_name = authors[0]
    for i in range(len(authors)):
        try:
            if authors[i][:len(prev_name)] == prev_name:
                authors[i] = authors[i][:len(prev_name)]

            if authors[i][:11] == 'kierkegaard' and not (authors[i] =='kierkegaard, søren'):
                authors[i] = authors[i] + ', søren'
                authors.pop(i + 1)

            titles[i] = titles[i][len(authors[i])+3:]

            if authors[i] == 'leibniz':
                authors[i] = 'gottfried wilhelm leibniz'
            elif authors[i] == 'hegel, gwf':
                authors[i] = 'hegel, g.w.f.'
            elif authors[i] == 'montaigne':
                authors[i] = 'michel de montaigne'
            elif authors[i] == 'st. augustine':
                authors[i] = 'st. augustine of hippo'
            elif authors[i] == 'spinoza':
                authors[i] = 'baruch spinoza'
            elif authors[i] == 'seneca':
                authors[i] = 'seneca the younger'
            elif authors[i] == 'confucius' or authors[i] == 'sun tzu':
                eastern_idxs.append(i)

            prev_name = authors[i]

            authors[i] = phils.standardize_name(authors[i])[0]

        except IndexError:
            break

    for i, idx in enumerate(eastern_idxs):
        authors.pop(idx - i)
        titles.pop(idx - i)


    print(len(authors))
    print(len(titles))
    print(len(links))

    return driver, authors, titles, links

if __name__ == '__main__':
    phils, docs = Philosophers(), Documents
    driver = init_driver()
    driver, authors, titles, links = get_initial_info(driver, phils)
