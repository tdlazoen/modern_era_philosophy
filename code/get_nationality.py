from dataframes import Philosophers, Documents
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from unidecode import unidecode
import numpy as np
import time

'''
This file tested out the webdriver method of
getting the nationaility and birthplaces
'''
def init_driver():
    driver = webdriver.Chrome()
    driver.wait = WebDriverWait(driver, 5)

    return driver

def nationality_birthplace(driver, name):
    query_nat = name + ' nationality'

    driver.get('https://www.google.com/')
    time.sleep(2)
    box = driver.wait.until(
            EC.presence_of_element_located((By.NAME, 'q'))
    )

    box.send_keys(query_nat)

    button = driver.wait.until(
                EC.element_to_be_clickable((By.NAME, 'btnG'))
    )

    button.click()

    time.sleep(2)

    try:
        nationality = driver.find_element_by_xpath('//*[@id="rso"]/div[1]/div[1]/div/div[1]/div[2]/div[2]/div/div[2]/div/div/div[1]')
        nationality = nationality.text.lower().strip()

    except NoSuchElementException:
        try:
            nationality = driver.find_element_by_xpath('//*[@id="uid_V_56oAAEBGwKVMWFIwPVsA_0"]/div/div/div[1]/div/div/a/div[2]/div/div/div')
            nationality = nationality.text.lower().strip()

        except NoSuchElementException:
                nationality = np.nan

    query_birth = name + ' philosopher birthplace'

    driver.get('https://www.google.com/')
    time.sleep(2)
    box = driver.wait.until(
            EC.presence_of_element_located((By.NAME, 'q'))
    )

    box.send_keys(query_birth)

    button = driver.wait.until(
                EC.element_to_be_clickable((By.NAME, 'btnG'))
    )

    button.click()

    time.sleep(2)

    try:
        birthplace = driver.find_element_by_xpath('//*[@id="uid_0"]/div[1]/div[2]/div[2]/div/div[2]/div/div/div[1]')
        birthplace = birthplace.text.lower().strip()

    except NoSuchElementException:
        try:
            birthplace = driver.find_element_by_xpath('//*[@id="rso"]/div[1]/div[1]/div/div[1]/div[2]/div[2]/div/div[2]/table/tbody/tr[4]/td[2]').text

            birthplace = birthplace.split()[-1].lower().strip()

        except NoSuchElementException:
            birthplace = np.nan

    return nationality, birthplace

if __name__ == '__main__':
    phils, docs = Philosophers(filepath='../data/philosophers.csv'), Documents(filepath='../data/documents.csv')
    phils.df['nationality'] = np.nan
    phils.df['birthplace'] = np.nan
    driver = init_driver()
    for i in range(phils.df.shape[0]):
        name = phils.df.loc[i, 'name']
        phils.df.loc[i, 'nationality'], phils.df.loc[i, 'birthplace'] = nationality_birthplace(driver, name)
    driver.quit()
