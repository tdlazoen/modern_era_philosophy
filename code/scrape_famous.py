'''
This file scrapes various websites for information about prominent philosophers
for various time periods
http://famous-philosophers.com/
https://en.wikipedia.org/wiki/17th-century_philosophy
https://en.wikipedia.org/wiki/Renaissance_philosophy
http://theculturetrip.com/europe/united-kingdom/articles/top-10-living-philosophers/
https://en.wikipedia.org/wiki/Hellenistic_philosophy
'''

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from collections import defaultdict
from dataframes import Philosophers, Documents
import re

def famous_philosophers(phils):
	url = 'http://famous-philosophers.com/'
	r = requests.get(url)
	soup = BeautifulSoup(r.content, 'html.parser')

	names = [unidecode(x.get_text().strip()) for x in soup.select('td a')]

	years = [filter(str.isdigit, re.split(r'[()]', x)[1]) for x in names]
	births = [int(x[:len(x)/2]) for x in years]
	deaths = [int(x[len(x)/2:]) for x in years]

	for i in range(len(names)):
	    if 'BC' in names[i]:
	        births[i] *= -1
	        deaths[i] *= -1

	names = [re.split(r'[()]', x)[0].strip() for x in names]

	idx = names.index('Confucius')
	names.pop(idx)
	births.pop(idx)
	deaths.pop(idx)
	idx1 = names.index('Gottfried Leibniz')
	idx2 = names.index('Thomas Aquinas')
	idx3 = names.index('Saint Augustine of Hippo')
	names[idx1] = 'Gottfried Wilhelm Leibniz'
	names[idx2] = 'St. Thomas Aquinas'
	names[idx3] = 'St. Augustine of Hippo'

	for i in range(len(names)):
		phils.add_philosopher_entry(names[i], births[i], deaths[i])

def renaissance_philosophers(phils):
	url = 'https://en.wikipedia.org/wiki/Renaissance_philosophy'
	get_philosophers(url, 'li', first_index=68, last_index=90)

def reason_philosophers(phils):
	url = 'https://en.wikipedia.org/wiki/17th-century_philosophy'
	get_philosophers(url, 'li', first_index=34, last_index=54)

def get_philosophers(url, tag, first_index, last_index):
	r = requests.get(url)
	soup = BeautifulSoup(r.content, 'html.parser')

	names_years = [unidecode(x.get_text().strip()) for x in soup.select(tag)[first_index:last_index]]

	try:
		names_years.remove('Mir Damad (d. 1631)')
	except ValueError:
		pass

	names = [re.split(r'[()]', x)[0].strip() for x in names_years]
	years = [filter(str.isdigit, re.split(r'[()]', x)[1].strip()) for x in names_years]
	births = [int(x[:len(x)/2]) for x in years]
	deaths = [int(x[len(x)/2:]) for x in years]

	if url == 'https://en.wikipedia.org/wiki/17th-century_philosophy':
		idx = names.index('Thomas Browne')
		births[idx] = 1605
		deaths[idx] = 1682

	for i in range(len(names)):
		phils.add_philosopher_entry(names[i], births[i], deaths[i])

def contemporary_philosophers(phils):
	url = 'http://theculturetrip.com/europe/united-kingdom/articles/top-10-living-philosophers/'
	r = requests.get(url)
	soup = BeautifulSoup(r.content, 'html.parser')

	name_years = [unidecode(x.get_text()) for x in soup.select('h3 strong')]
	names = [re.split(r'[()]', x)[0].strip() for x in name_years]
	births = [int(filter(str.isdigit, re.split(r'[()]', x)[1])) for x in name_years]

	for i in range(len(names)):
		phils.add_philosopher_entry(names[i], births[i], np.nan, time_period='contemporary')

def hellenistic_philosophers(phils):
	url = 'https://en.wikipedia.org/wiki/Hellenistic_philosophy'
	r = requests.get(url)
	soup = BeautifulSoup(r.content, 'html.parser')

	names_years = [unidecode(x.get_text().strip()) for x in soup.select('li')[17:71]]
	k = 0
	for i in range(len(names_years)):
	    if 'century' in names_years[i-k] or 'c.' in names_years[i-k]:
	        names_years.remove(names_years[i-k])
	        k += 1

	names = [re.split(r'[()]', x)[0].strip() for x in names_years]
	names.remove('Pythagoras of Croton')
	years = [filter(str.isdigit, re.split(r'[()]', x)[1].strip()) for x in names_years]
	births = [int(x[:len(x)/2]) for x in years]
	deaths = [int(x[len(x)/2:]) for x in years]

	for i in range(len(names_years)):
	    if 'BCE' in names_years[i]:
	        births[i] *= -1
	        deaths[i] *= -1

	idx1 = names.index('Philo of Alexandria')
	births[idx1] = -30
	deaths[idx1] = 45
	idx2 = names.index('Seneca the Younger')
	births[idx2] = -4
	deaths[idx2] = 65
	idx3 = names.index('Cicero')
	names[idx3] = 'Marcus Tullius Cicero'
	idx4 = names.index('Augustine of Hippo')
	names[idx4] = 'St. Augustine of Hippo'

	for i in range(len(names)):
		if names[i] == 'Varro Reatinus':
			births[i] = -116
			deaths[i] = -127

		phils.add_philosopher_entry(names[i], births[i], deaths[i])

if __name__ == '__main__':
	phils = Philosophers()
	# famous_philosophers(phils)
	# renaissance_philosophers(phils)
	# reason_philosophers(phils)
	# contemporary_philosophers(phils)
	# hellenistic_philosophers(phils)
