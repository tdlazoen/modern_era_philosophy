import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
import urllib
import re
import os

class Philosophers(object):

	def __init__(self):
		self.df = pd.read_csv('../data/philosophers.csv')
		self.philosophers = self.df['name']
		self.filepath = '../data/philosophers.csv'

	def add_philosopher_entry(self, name, birth, death, time_period=None):
			'''
			Add a new philosopher to the dataframe
			'''
			name, filepath = self.standardize_name(name, image=True)

			if time_period is None:
				time_period = self.determine_time_period(birth, death)

			era = self.determine_era(time_period)
			century = self.determine_century(birth, death)

			new_entry = {'name': name,
						 'year_born': birth,
						 'year_died': death,
						 'century': century,
						 'time_period': time_period,
						 'era': era,
						 'image_path': filepath}

			self.df = self.df.append(new_entry, ignore_index=True)

	def determine_time_period(self, birth, death):
		'''
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
			urllib.urlretrieve(url, filepath)

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

class Documents(object):

	def __init__(self):
		self.df = pd.read_csv('../data/documents.csv')
		self.docs = self.df['title']
		self.filepath = '../data/documents.csv'

	def add_document(self, author, title, year, text, url, filename=None):
		'''
		Add new document to the documents dataframe
		'''
		new_entry = {'title': title,
					 'author': author,
					 'year': year,
					 'text': text,
					 'url': url,
					 'filename': filename}

		self.df = self.df.append(new_entry, ignore_index=True)

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
