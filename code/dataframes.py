import numpy as np
import pandas as pd

class Philosophers(object):

	def __init__(self):
		self.df = pd.read_csv('../data/philosophers.csv')
		self.philosophers = self.df['name']
		self.filepath = '../data/philosophers.csv'

	def add_philosopher_entry(self, name, birth, death, nationality=None):
			'''
			Add a new philosopher to the dataframe
			'''
		    name, filepath = self.standardize_name(name, image=True)
			time_period = self.determine_time_period(birth)
			year_born = birth
			year_died = death

			new_entry = {'name': name,
						 'nationality': nationality,
						 'time_period': time_period
						 'year_born': year_born,
						 'year_died': year_died
						 'image_path': filepath}

			self.df.append(new_entry, ignore_index=True)

	def determine_time_period(self, birth):
		'''
		Determine the time period of a philosopher given
		their birth year
		'''
	    time_periods = np.unique(self.df['time_period'])
	    for time_period in time_periods:
	        years = time_periods[time_periods == time_period]
	        min_year = np.min(years) - 20
	        max_year = np.max(years) + 20

	        if birth in range(min_year, max_year):
	            return time_period

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
	        get_image(new_name.strip(), filepath)

	    return new_name.strip(), filepath

	def update_df(self, df):
		'''
		upadate class dataframe to newly changed dataframe
		'''
		self.df = df

	def save_df(self, filepath=None):
		'''
		Save dataframe to filepath specified
		'''
		if filepath:
			self.filepath = filepath
		path = filepath
		self.df.to_csv(self.filepath)

class Documents(object):

	def __init__(self):
		self.df = pd.read_csv('../data/documents.csv')
		self.docs = self.df['title']
		self.filename = '../data/documents.csv'

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

		self.df.append(new_entry, ignore_index=True)

	def update_df(self, df):
		'''
		upadate class dataframe to newly changed dataframe
		'''
		self.df = df

	def save_df(self, filepath=None):
		'''
		Save dataframe to filepath specified
		'''
		if filepath:
			self.filepath = filepath
		path = filepath
		self.df.to_csv(self.filepath)
