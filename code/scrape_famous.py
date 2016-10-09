'''
This file scrapes various websites for information about prominent philosophers
for various time periods
http://famous-philosophers.com/
https://en.wikipedia.org/wiki/17th-century_philosophy
https://en.wikipedia.org/wiki/Renaissance_philosophy
http://theculturetrip.com/europe/united-kingdom/articles/top-10-living-philosophers/
http://www.logicmuseum.com/wiki/List_of_medieval_philosophers
http://www.logicmuseum.com/wiki/List_of_medieval_philosophers
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

	for i in xrange(len(names)):
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

	for i in xrange(len(names)):
		if names[i] not in phils.df['name'].values:
			phils.add_philosopher_entry(names[i], births[i], deaths[i])

def medieval_philosophers(phils):
	url = 'http://www.logicmuseum.com/wiki/List_of_medieval_philosophers'
	r = requests.get(url)
	soup = BeautifulSoup(r.content, 'html.parser')

	names = [unidecode(x.get_text().strip()) for x in soup.select('td a')]
	idx = names.index('Anselm')
	names[idx] = 'St. Anselm'

	births = [unidecode(x.get_text().strip()) for x in soup.select('tr td')[1::6]]
	births = [filter(str.isdigit, x)[:4] for x in births]
	births = [np.nan if x == '' else int(x) for x in births]

	deaths = [unidecode(x.get_text().strip()) for x in soup.select('tr td')[4::6]]
	deaths = [filter(str.isdigit, x)[:4] for x in deaths]
	deaths = [np.nan if x == '' else int(x) for x in deaths]

	for i in xrange(len(names)):
		if names[i] not in phils.df['name'].values:
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

	for i in xrange(len(names)):
		if names[i] not in phils.df['name'].values:
			phils.add_philosopher_entry(names[i], births[i], deaths[i])

def contemporary_philosophers(phils):
	url = 'http://theculturetrip.com/europe/united-kingdom/articles/top-10-living-philosophers/'
	r = requests.get(url)
	soup = BeautifulSoup(r.content, 'html.parser')

	name_years = [unidecode(x.get_text()) for x in soup.select('h3 strong')]
	names = [re.split(r'[()]', x)[0].strip() for x in name_years]
	births = [int(filter(str.isdigit, re.split(r'[()]', x)[1])) for x in name_years]

	for i in xrange(len(names)):
		if names[i] not in phils.df['name'].values:
			phils.add_philosopher_entry(names[i], births[i], np.nan, time_period='contemporary')

if __name__ == '__main__':
	phils = Philosophers()
	# famous_philosophers(phils)
	# renaissance_philosophers(phils)
	# reason_philosophers(phils)
	# contemporary_philosophers(phils)
	medieval_philosophers(phils)
