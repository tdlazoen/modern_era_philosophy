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
from selenium.common.exceptions import NoSuchElementException
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
	'''
	Allows for easy accessing and updating/saving of
	dataframe containing all modern era philosophers
	'''
	def __init__(self, filepath='data/modern_philosophers.csv'):
		'''
		Parameters:
			filepath - The filepat the csv file will be saved to
		'''
		self.df = pd.read_csv(filepath)
		self.philosophers = self.df['name']
		self.filepath = filepath
		self.driver = None

	def add_philosopher_entry(self, name, birth=None, death=None, time_period=None):
		'''
		INPUT:
			name - name of philosopher
			birth - year of philosopher's birth.  If None, determined through
					function get_lifespan
			death - year of philosopher's death.  If None, determined through
					function get_lifespan
			time_period - time period of philosopher.  If None, determined through
						  function determine_time_period
		OUTPUT:
			None

		Add a new philosopher to the dataframe
		'''
		name, filepath = self.standardize_name(name, image=True)

		if birth is None and death is None:
			birth, death = self.get_lifespan(name)

		if time_period is None:
			time_period = self.determine_time_period(birth, death)

		if name not in self.df.name.values:
			era = 'modern'
			century = self.determine_century(birth, death)

			nationality = self.get_nationality(name)
			birthplace = self.get_birthplace(name)

			if nationality == 'american' and birthplace:
				birthplace = self.american_birthplaces(birthplace)

			country = re.split('\,', birthplace)[-1].strip()

			new_entry = {'name': name,
						 'nationality': nationality,
						 'birthplace': birthplace,
						 'country': country,
						 'year_born': birth,
						 'year_died': death,
						 'century': century,
						 'time_period': time_period,
						 'era': era,
						 'image_path': filepath}

			self.df = self.df.append(new_entry, ignore_index=True)
		else:
			print('The philosopher {} already exists!'.format(name))

	def determine_time_period(self, birth, death):
		'''
		INPUT:
			birth - year of philosopher's birth
			death - year of philosopher's death
		OUTPUT:
			time period of philospher

		Determine the time period of a philosopher given
		their birth and death year
		'''
		time_periods = np.unique(self.df['time_period'])
		diffs = []
		for time_period in time_periods:
			tp_df = self.df[self.df['time_period'] == time_period]
			birth_diff = np.abs(birth - tp_df['year_born'].median())
			death_diff = np.abs(death - tp_df['year_died'].median())
			diffs.append(birth_diff + death_diff)

		return time_periods[diffs.index(np.nanmin(diffs))]

	def determine_century(self, year_born, year_died):
		'''
		INPUT:
			year_born = year of philosopher's birth
			year_died = year of philosopher's death
		OUTPUT:
			the century the philosopher was likely most active during

		Determine century philosopher was most prominent in based on birth and death years
		'''
		if year_born < 1900:
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
		INPUT:
			name - name of philosopher
		OUTPUT:
			nationality that was found by running a google search with
			selenium web driver

		Attempt to get the nationality of the philosopher
		'''
		query_nat = name + ' nationality'

		self.run_google_query(query_nat)

		try:
			nationality = self.driver.find_element_by_xpath('//*[@id="rso"]/div[1]/div[1]/div/div[1]/div[2]/div[2]/div/div[2]/div/div/div[1]')
			nationality = nationality.text.lower().strip()

		except NoSuchElementException:
			try:
				nationality = self.driver.find_element_by_xpath('//*[@id="uid_V_56oAAEBGwKVMWFIwPVsA_0"]/div/div/div[1]/div/div/a/div[2]/div/div/div')
				nationality = nationality.text.lower().strip()

			except NoSuchElementException:
				nationality = ''

		return nationality

	def get_birthplace(self, name):
		'''
		INPUT:
			name - name of philosopher
		OUTPUT:
			nationality found using a google search with selenium

		Attempt to get the birthplace of a philosopher
		'''
		query_birth = name + ' philosopher birthplace'

		self.run_google_query(query_birth)

		try:
			birthplace = self.driver.find_element_by_xpath('//*[@id="uid_0"]/div[1]/div[2]/div[2]/div/div[2]/div/div/div[1]')
			birthplace = birthplace.text.lower().strip()

		except NoSuchElementException:
			try:
				birthplace = self.driver.find_element_by_xpath('//*[@id="rso"]/div[1]/div[1]/div/div[1]/div[2]/div[2]/div/div[2]/table/tbody/tr[4]/td[2]').text

				birthplace = birthplace.split()[-1].lower().strip()

			except NoSuchElementException:
				birthplace = ''

		self.driver.quit()
		return birthplace

	def get_lifespan(self, name):
		'''
		INPUT:
			name - name of philosopher
		OUTPUT:
			birth_year - google search result of birth year for philosopher
			death_year - google search result of death year for philosopher

		Attempt to get the years of birth and deathof a philosopher
		'''
		self.driver = self.init_driver()

		for i, query in enumerate([' year of birth', ' year of death']):
			query_phil = name + query

			self.run_google_query(query_phil)

			if i == 0:
				try:
					birth_year = self.driver.find_element_by_xpath('//*[@id="rso"]/div[1]/div[1]/div/div[1]/div[2]/div[2]/div/div[2]/div/div/div[1]')
					birth_year = re.split('\,', birth_year.text)[-1].lower().strip()
					birth_year = int(''.join(x for x in birth_year if x.isdigit()))

				except NoSuchElementException:
					birth_year = 0
			else:
				try:
					death_year = self.driver.find_element_by_xpath('//*[@id="rso"]/div[1]/div[1]/div/div[1]/div[2]/div[2]/div/div[2]/div/div/div[1]')
					death_year = re.split('\,', death_year.text)[-1].lower().strip()
					death_year = int(''.join(x for x in death_year if x.isdigit()))

				except NoSuchElementException:
					death_year = 0

		return birth_year, death_year

	def american_birthplaces(self, birthplace):
		'''
		INPUT:
			birthplace - birthplace of philosopher
		OUTPUT:
			If country of birth is America; reformats from (city, state) to
											(state, united states)
			Otherwise; returns birthplace
		'''
		try:
			birthplace_state = re.split(r',', birthplace)[-1].strip()
			if len(birthplace_state) > 2:
				return birthplace
			return us.states.lookup(birthplace_state).name.lower() + ', united states'
		except AttributeError:
			return birthplace

	def standardize_name(self, name, image=False):
		'''
		INPUT:
			name - name of philosopher
			image - whether to find an image for philosopher or not
					(see function get_image)
		OUTPUT:
			Name in following format: (title) First Last

		Standardize names to format used throughout dataframe
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
		INPUT: filepath to save image to
		OUTPUT: filepath of image file

		Saves the image of given philosopher and returns filepath
		image was saved to
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
		INPUT:
			df - dataframe
		OUTPUT:
			None

		Upadate self.df to the dataframe passed
		'''
		self.df = df

	def save_df(self, filepath=None):
		'''
		INPUT:
			filepath - path to save dataframe to. Updates self.filepath
		OUTPUT:
			None

		Save dataframe to filepath specified
		'''
		if not (filepath is None):
			self.filepath = filepath
		self.df.to_csv(self.filepath, index=False)

	def init_driver(self):
		'''
		INPUT:
			None
		OUTPUT:
			driver - selenium chrome web driver

		Initialize selenium web driver
		'''
		driver = webdriver.Chrome()
		driver.wait = WebDriverWait(driver, 5)

		return driver

	def run_google_query(self, query):
		'''
		INPUT:
			query - the desired query to search on googles
		OUTPUT:
			None

		Runs a google search using the query passed
		'''
		self.driver.get('https://www.google.com/')
		time.sleep(2)
		box = self.driver.wait.until(
				EC.presence_of_element_located((By.NAME, 'q'))
		)

		box.send_keys(query)

		button = self.driver.wait.until(
				EC.element_to_be_clickable((By.NAME, 'btnG'))
		)

		button.click()

		time.sleep(2)


class ModernDocuments(object):
	'''
	Allows for easy accessing and updating/saving of
	dataframe containing all documents written by modern era
	philosophers
	'''
	def __init__(self, filepath='data/modern_documents.csv'):
		'''
		Parameters:
			filepath - The filepat the csv file will be saved to
		'''
		self.df = pd.read_csv(filepath)
		self.docs = self.df['title']
		self.filepath = filepath

	def add_document(self, author, title, year, text, url, filepath=None):
		'''
		INPUT:
			author - document author
			title - document title
			year - document year
			text - full text of document
			url - source of document text
			filepath - filepath of document (if file)
					   None if text isn't saved in file form
		OUTPUT:
			None

		Add new document to the documents dataframe
		'''
		# Get cleaned text
		text = self.clean_text(text)

		# Get number of words
		num_words = self.get_num_words(text)

		# Get century of document
		century = year - (year % 100)

		# Check if title exists already by the author
		auth_df = self.df[self.df.author == author]
		if title not in auth_df.title.values:
			# Create new entry and add to dataframe
			new_entry = {'title': title,
						 'author': author,
						 'year': year,
						 'century': century,
						 'text': text,
						 'words': num_words,
						 'url': url,
						 'filepath': filepath}

			self.df = self.df.append(new_entry, ignore_index=True)

		else:
			print('Document {} already exists!'.format(title))

	def clean_text(self, text):
		'''
		INPUT:
			text - full text of a document
		OUTPUT:
			Text that has been cleaned of unneccessary characters
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
		'''
		INPUT:
			text - full text of a document
		OUTPUT:
			Number of words in document
		'''
		return len(text.split())

	def update_df(self, df):
		'''
		INPUT:
			df - dataframe
		OUTPUT:
			None

		Upadate self.df to the dataframe passed
		'''
		self.df = df

	def save_df(self, filepath=None):
		'''
		INPUT:
			filepath - path to save dataframe to. Updates self.filepath
		OUTPUT:
			None

		Save dataframe to filepath specified
		'''
		if not (filepath is None):
			self.filepath = filepath
		self.df.to_csv(self.filepath, index=False)
