import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from string import punctuation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import urllib
import re
import os
import us

'''
Classes utilized for easily editing and accessing
the philosopher and document dataframes
'''

class ModernPhilosophers(object):

	def __init__(self, filepath='../data/modern_philosophers.csv'):
		self.df = pd.read_csv(filepath)
		self.philosophers = self.df['name']
		self.filepath = filepath

	def add_philosopher_entry(self, name, birth, death, time_period='modern'):
			'''
			Add a new philosopher to the dataframe
			'''
			name, filepath = self.standardize_name(name, image=True)

			if name not in self.df.name.values:
				era = self.determine_era(time_period)
				century = self.determine_century(birth, death)

				nationality = self.get_nationality(name)
				birthplace = self.get_birthplace(name)

				if nationality == 'american' and birthplace:
					birthplace = self.american_birthplaces(birthplace)

				new_entry = {'name': name,
							 'nationality': nationality,
							 'birthplace': birthplace,
							 'year_born': birth,
							 'year_died': death,
							 'century': century,
							 'time_period': time_period,
							 'era': era,
							 'image_path': filepath}

				self.df = self.df.append(new_entry, ignore_index=True)
			else:
				print('The philosopher {} already exists!'.format(name))

	def determine_era(self, time_period):
		'''
		Returns the era of a philosopher given their
		time period.
		'''
		if time_period in ['presocratic', 'socratic', 'hellenistic', 'roman']:
			return 'ancient'
		elif time_period in ['medieval', 'renaissance']:
			return 'medieval'
		elif time_period == 'contemporary':
			return 'contemporary'
		else:
			return 'modern'

	def determine_century(self, year_born, year_died):
		if year_born < 0:
			if year_died + (abs(year_died) % 100) == year_born + (abs(year_born) % 100):
				return year_born + (abs(year_born) % 100)

			elif abs(year_born) % 100 > 25:
				return year_born + (abs(year_born) % 100)

			else:
				return (year_born + 100) + (abs(year_born) % 100)

		elif year_born < 1900:
			if year_died - (year_died % 100) == year_born - (year_born % 100):
				return year_born - (year_born % 100)

			elif year_born % 100 < 50:
				return year_born - (year_born % 100)

			else:
				return (year_born + 100) - (year_born % 100)

		else:
			if year_died - (year_died % 100) == year_born - (year_born % 100):
				return year_born - (year_born % 100)

			elif year_born % 100 < 35:
				return year_born - (year_born % 100)
			else:
				return (year_born + 100) - (year_born % 100)

	def get_nationality(self, name):
		'''
		Attempt to get the nationality of the philosopher
		'''
		query_nat = name + ' nationality'

		driver = webdriver.Chrome()
		driver.wait = WebDriverWait(driver, 5)

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

		driver.quit()
		return nationality

	def get_birthplace(self, name):
		'''
		Attempt to get the birthplace of a philosopher
		'''
		query_birth = name + ' philosopher birthplace'

		driver = webdriver.Chrome()
		driver.wait = WebDriverWait(driver, 5)

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

		driver.quit()
		return birthplace

	def american_birthplaces(self, birthplace):
		try:
			birthplace_state = re.split(r',', birthplace)[-1].strip()
			if len(birthplace_state) > 2:
				return birthplace
			return us.states.lookup(birthplace_state).name.lower() + ', united states'
		except AttributeError:
			return birthplace

	def standardize_name(self, name, image=False):
		'''
		Standardize name to format used throughout dataframe
		'''
		if 'Sir' in name:
			components = re.split(r', Sir ', name)
		else:
			components = re.split(r',', name)

		new_name = ' '.join(x for x in components[::-1])

		try:
			start = new_name.index('(')
			end = new_name.index(')')

			new_name = new_name[:start-1] + new_name[end+1:]

		except ValueError:
			pass

		filepath = os.path.expanduser('~') + '/philosophy_capstone/images/' + new_name.strip().lower().replace(' ', '_') + '.jpg'

		if image:
			self.get_image(new_name.strip(), filepath)

		return new_name.strip(), filepath

	def get_image(self, name, filepath):
		'''
		Saves the image of given philosopher and returns filepath
		INPUT: filepath to save image to
		OUTPUT: filepath of image file
		'''
		# Google images url with search terms of name
		img_url = '''https://www.google.com/search?site=imghp&tbm=isch&source=hp&biw=1440&bih=803&q={}&oq={}&
	                    gs_l=img.3..0l10.1021.2400.0.2681.10.7.0.3.3.0.82.519.7.7.0....0...
	                    1ac.1.64.img..0.10.523.IxXhEvSJyAw
	               '''.format(name, name)
	    # Request url
		r = requests.get(img_url)
		soup = BeautifulSoup(r.content, 'html.parser')

	    # Unidecode source url
		url = unidecode(soup.img['src'])

		# Save image to inputted filepath
		if filepath not in self.df['image_path'].values:
			urllib.request.urlretrieve(url, filepath)

	def update_df(self, df):
		'''
		upadate class dataframe to newly changed dataframe
		'''
		self.df = df

	def save_df(self, filepath=None):
		'''
		Save dataframe to filepath specified
		'''
		if not (filepath is None):
			self.filepath = filepath
		self.df.to_csv(self.filepath, index=False)

class ModernDocuments(object):

	def __init__(self, filepath='../data/modern_documents.csv'):
		self.df = pd.read_csv(filepath)
		self.docs = self.df['title']
		self.filepath = filepath

	def add_document(self, author, title, year, text, url, filepath=None):
		'''
		Add new document to the documents dataframe
		'''
		text = self.clean_text(text)
		num_words = self.get_num_words(text)

		if title not in self.df.title.values:
			new_entry = {'title': title,
						 'author': author,
						 'year': year,
						 'text': text,
						 'words': num_words,
						 'url': url,
						 'filepath': filepath}

			self.df = self.df.append(new_entry, ignore_index=True)

		else:
			print('Document {} already exists!'.format(title))

	def clean_text(self, text):
		'''
		Clean text of a document
		'''

		text = text.strip(punctuation)

		if not(text.isalpha()):
			text_lst = text.split()

		for i in range(len(text_lst)):
			if not(text_lst[i].isalpha()):
				text_lst[i] = ''.join(x for x in text_lst[i] if x.isalpha())

		text = ' '.join(word for word in text_lst)

		return text.lower()

	def get_num_words(self, text):
		return len(text.split())

	def update_df(self, df):
		'''
		upadate class dataframe to newly changed dataframe
		'''
		self.df = df

	def save_df(self, filepath=None):
		'''
		Save dataframe to filepath specified
		'''
		if not (filepath is None):
			self.filepath = filepath
		self.df.to_csv(self.filepath, index=False)
