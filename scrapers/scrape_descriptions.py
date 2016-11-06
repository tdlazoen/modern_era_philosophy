from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import numpy as np
import re
import os
import sys
sys.path.append(os.path.abspath('..'))
from modern_dfs import ModernPhilosophers


'''
This file scrapes wikipedia pages for each philosoher in the philsophers
dataframe for a short summary describing that philosopher's feats/life.
'''


def get_descriptions(name):
    '''
    INPUT:
        name - name of philosopher
    OUTPUT:
        description - short summary of philosopher's significance

    Retrieves description for given philosopher
    philosopher dataframe
    '''
    driver = init_driver()
    driver.get('https://www.google.com')

    box = driver.wait.until(
            EC.presence_of_element_located((By.NAME, 'q'))
    )
    box.send_keys(name)
    box.submit()

    try:
        wiki_link = driver.wait.until(
                EC.element_to_be_clickable((By.XPATH,
                        '/html/body//h3/a[text()[contains(., "Wikipedia")]]'))
        )
        wiki_link.click()
    except TimeoutException:
            box = driver.wait.until(
                    EC.presence_of_element_located((By.NAME, 'q'))
            )
            box.send_keys(name + 'philosopher')
            box.submit()

            wiki_link = driver.wait.until(
                    EC.element_to_be_clickable((By.XPATH,
                            '/html/body//h3/a[text()[contains(., "Wikipedia")]]'))
            )
            wiki_link.click()

    par = driver.wait.until(
            EC.presence_of_element_located((By.XPATH,
                    '//*[@id="mw-content-text"]/p[1]'))
    )
    summary = par.text

    summary = remove_text_inside_brackets(summary)

    comma_summary = ''
    for word in summary.split():
        if word.find(',') == 0:
            comma_summary += word
        else:
            comma_summary += (' ' + word)

    driver.quit()
    print('\n' + comma_summary.strip())
    return comma_summary.strip()


def remove_text_inside_brackets(text, brackets="()[]"):
    '''
    INPUT:
        text - text to clean
        brackets - the types of brackets to look for
    OUTPUT:
        text with all texts within brackets removed

    Removes text within bracket character
    '''
    count = [0] * (len(brackets) // 2) # count open/close brackets
    saved_chars = []
    for character in text:
        for i, b in enumerate(brackets):
            if character == b: # found bracket
                kind, is_close = divmod(i, 2)
                count[kind] += (-1)**is_close # `+1`: open, `-1`: close
                if count[kind] < 0: # unbalanced bracket
                    count[kind] = 0
                break
        else: # character is not a bracket
            if not any(count): # outside brackets
                saved_chars.append(character)
    return ''.join(saved_chars)


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


if __name__ == '__main__':
    phils = ModernPhilosophers(filepath='../data/modern_philosophers.csv')
    phils.df['summary'] = np.nan
    for i in range(phils.df.shape[0]):
        name = phils.df.loc[i, 'name']
        phils.df.loc[i, 'summary'] = get_descriptions(name)
