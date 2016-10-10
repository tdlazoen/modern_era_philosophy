import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from collections import defaultdict
from dataframes import Philosophers, Documents
import re

def scrape_sacred():
	base_url = 'http://sacred-texts.com/phi/'
	r = requests.get(base_url)
	soup = BeautifulSoup(r.content, 'lxml')

	names = [unidecode(x.get_text().strip()) for x in soup.select('h3')][:-1]
	names.remove('Epicurus')
	new_names = []
	titles_dates = [unidecode(x.get_text()) for x in soup.select('span.c_e')]
	links = [unidecode(x['href']).strip() for x in soup.select('span.c_e a')]
	links

	i = 0
	titles = []
	dates = []

	for name in names:

	    if i == 70:
	        break
	    link_base = re.split(r'/', links[i])[0]

	    for entry in titles_dates[i:]:

	        if link_base in links[i]:
	            if i == 9:
	                name = 'Epicurus'

	            new_names.append(name)

	            title = re.split(r'[[\]]', entry)[0].strip()

	            if title == 'Discourse on the Method of Rightly Conducting the Reason, and Seeking Truth in the Sciences':
	                title = 'Discourse on the Method'

	            try:
	                date = re.split(r'[[\]]', entry)[1]
	                if 'BCE' in date:
	                    date = -1 * int(filter(str.isdigit, date))
	                else:
	                    date = int(filter(str.isdigit, date))
	                dates.append(date)
	            except IndexError:
	                dates.append(0)
	            titles.append(title)
	            i += 1
	        else:
	            break

	links = ['http://sacred-texts.com/phi/' + x for x in links]
	links = [x.replace('phi/../', '') if '..' in x else x for x in links]
	idxs = [links.index(x) for x in links if 'spinoza' in x]
	for i, idx in enumerate(idxs):
	    new_names.pop(idx-i)
	    titles.pop(idx-i)
	    dates.pop(idx-i)
	    links.pop(idx-i)

	return new_names, titles, dates, links

def merge_parts(docs):
	last_title = docs.df.title.values[0]
	for title in docs.df.title.values[1:]:
	    if last_title[:8] in title:
	        print title
	    last_title = title

	part_texts = ['leviathan', 'essay concerning human understanding', 'new essays on human understanding', 'essays on the intellectual powers of man', 'essays on the active powers of man', 'a treatise of human nature', 'an inquiry into the nature and causes of the wealth of nations', 'the critique of pure reason', 'a system of logic']

	for text_name in part_texts:
	    lst_title = [x for x in docs.df.title.values if x[:len(text_name)] == text_name]
	    idxs = [docs.df[docs.df.title == x].index[0] for x in lst_title]
	    author = docs.df.loc[idxs[0], 'author']
	    year = docs.df.loc[idxs[0], 'year']
	    text = ''
	    pdfs = []
	    urls = []
	    for idx in idxs:
	        text += docs.df.loc[idx, 'text']
	        pdfs.append(docs.df.loc[idx, 'filepath'])
	        urls.append(docs.df.loc[idx, 'url'])

	    new_entry = {'title': text_name,
	                 'author': author,
	                 'year': year,
	                 'text': text,
	                 'url': urls,
	                 'filepath': pdfs}
	    docs.df = docs.df.append(new_entry, ignore_index=True)
	    docs.df.drop(idxs, inplace=True)

		docs.save_df()

if __name__ == '__main__':
	phils, docs = Philosophers(filepath='../data/philosophers.csv'), Documents(filepath='../data/documents.csv')
