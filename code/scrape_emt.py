import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from collections import defaultdict
from itertools import izip
from string import punctuation
import urllib
import os
import re
import time
import philosopher_profile_data as ppd
'''
------- Originally used for python 2 ---------
from cStringIO import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
'''
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
import pandas as pd
import numpy as np

'''
This file scapes the website Early Modern Philosophy
http://www.earlymoderntexts.com/texts
'''

def add_to_philosophers_dict(phil_dict):
	'''
	Add Newly acquired philosopher names into philosopher
	dictionary if not already existing in it
	'''
	# Request from url
	url = 'http://www.earlymoderntexts.com/texts'
	time.sleep(1)
	r = requests.get(url)
	soup = BeautifulSoup(r.content, 'html.parser')

	# Get names of each author
	authors = [unidecode(x.string) for x in soup.select('li b')]

	# Remove non-philosophers / ones with no texts
	authors.remove('Isaac Newton (1642-1727)')
	authors.remove('Sophie de Grouchy (1764-1822)')

	# Find the birth and death dates of each philosopher
	years = [filter(str.isdigit, x) for x in authors]
	lifespans = [(x[:4], x[4:]) for x in years]
	birth_years = [int(x[0]) for x in lifespans]
	death_years = [int(x[1]) for x in lifespans]

	# Remove years from author names
	authors = [re.split(r'[()]', x)[0].strip() for x in authors]

	# Shorten name
	idx = authors.index('Anthony Ashley Cooper, third Earl of Shaftesbury')
	authors[idx] = 'Anthony Ashley Cooper'

	# Add philosophers to the philospher dictionary
	for i in range(len(authors)):
	    if authors[i] not in phil_dict.keys():
	        phil_dict = ppd.add_new(phil_dict, authors[i], birth_years[i], death_years[i])

	return phil_dict, authors

def add_document(dct, author, title, year, url, filepath=None):
	'''
	Add new document to the documents list
	'''
	idx = len(dct)
	dct[idx]['title'] = title
	dct[idx]['author'] = author
	dct[idx]['year'] = year
	dct[idx]['pdf_url'] = url
	if filepath:
		dct[idx]['pdf_file'] = filepath

	return dct

def get_pdfs(author):
	'''
	Get information to download an author's pdfs
	'''
    base_link = 'http://www.earlymoderntexts.com/authors/'
    author_link = None

	# Account for inconsistencies
    if author == 'Julien Offray de La Mettrie':
        author_link = base_link + 'lamettrie'

    elif author == 'Anthony Ashley Cooper':
        author_link = base_link + 'shaftesbury'

    else:
        name_split = author.split()
        last_name = name_split[-1].lower().strip()
        author_link = base_link + last_name

	# Request from author url
    url = author_link
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

	# Get author's name
    text_author = unidecode(soup.select('div.content h2')[0].get_text())
    text_author = re.split(r',', text_author)[0]

	# Get all titles
    titles = [unidecode(x.get_text()) for x in soup.select('li b')]

	# Account for inconsistencies
    if author == 'Thomas Hobbes':
        title = titles[0]
        titles = []
        for i in range(1, 5):
            titles.append(title + ' Part {}'.format(i))

    elif author == 'John Locke':
        idx = titles.index('Essay Concerning Human Understanding')
        for i in range(1, 5):
            title = 'Essay Concerning Human Understanding' + ' Part {}'.format(i)
            titles.insert(idx + (i-1), title)
        titles.remove('Essay Concerning Human Understanding')

    elif author == 'Gottfried Wilhelm Leibniz':
        idx = titles.index('New Essays on Human Understanding')
        for i in range(1, 5):
            title = 'New Essays on Human Understanding' + ' Book {}'.format(i)
            titles.insert(idx + (i-1), title)
        titles.remove('New Essays on Human Understanding')

    elif author == 'Thomas Reid':
        idx1 = titles.index('Essays on the Intellectual Powers of Man')

        for i in range(1, 8):
            title = 'Essays on the Intellectual Powers of Man' + ' Essay {}'.format(i)
            titles.insert(idx1 + (i-1), title)

        idx2 = titles.index('Essays on the Active Powers of Man')

        for i in range(1, 6):
            title = 'Essays on the Active Powers of Man' + ' Essay {}'.format(i)
            titles.insert(idx2 + (i-1), title)

        titles.remove('Essays on the Intellectual Powers of Man')
        titles.remove('Essays on the Active Powers of Man')

    elif author == 'David Hume':
        idx = titles.index('A Treatise of Human Nature')
        books = ['I', 'II', 'III']

        for i, book in enumerate(books):
            title = 'A Treatise of Human Nature' + ' Book ' + book
            titles.insert(idx + (i), title)

        titles.remove('A Treatise of Human Nature')

    elif author == 'Adam Smith':
        idx = titles.index('An Inquiry into the Nature and Causes of the Wealth of Nations')
        books = ['Book I', 'Book II', 'Books III and IV', 'Book V']

        for i, book in enumerate(books):
            title = 'An Inquiry into the Nature and Causes of the Wealth of Nations' + ' ' + book
            titles.insert(idx + (i), title)

        titles.remove('An Inquiry into the Nature and Causes of the Wealth of Nations')

    elif author == 'Immanuel Kant':
        idx = titles.index('The Critique of Pure Reason')
        parts = ['First Part', 'Second Part']

        for i, part in enumerate(parts):
            title = 'The Critique of Pure Reason' + ' ' + part
            titles.insert(idx + (i), title)

        titles.remove('The Critique of Pure Reason')

    elif author == 'John Stuart Mill':
        idx1 = titles.index('A System of Logic')
        books = ['I', 'II', 'III', 'IV']

        for i, book in enumerate(books):
            title = 'A System of Logic' + ' Book ' + book
            titles.insert(idx1 + (i), title)

        idx2 = titles.index('Three Essays on Religion')
        books = ['Helen Taylor\'s Introduction to the Essays', 'Nature', 'The Usefulness of Religion', \
                'Theism']

        for i, book in enumerate(books):
            title = book
            titles.insert(idx2 + (i), title)

        titles.remove('A System of Logic')
        titles.remove('Three Essays on Religion')

    long_titles = [unidecode(x.get_text()) for x in soup.select('li')]
    year_pub = []

	# Get year each title was published
    for title in titles:
		# Accounting for inconsistencies
        if author == 'Thomas Hobbes':
            year_pub.append(1651)
            continue
        elif title[:36] == 'Essay Concerning Human Understanding' and author == 'John Locke':
            year_pub.append(1690)
            continue

        elif title[:33] == 'New Essays on Human Understanding' and author == 'Gottfried Wilhelm Leibniz':
            year_pub.append(1705)
            continue

        elif author == 'Thomas Reid':
            if title[:34] == 'Essays on the Active Powers of Man':
                year_pub.append(1788)
                continue

            elif title[:40] == 'Essays on the Intellectual Powers of Man':
                year_pub.append(1785)
                continue
            else:
                title = title

        elif author == 'David Hume' and title[:26] == 'A Treatise of Human Nature':
            year_pub.append(1739)
            continue

        elif author == 'Adam Smith' and 'An Inquiry into the Nature and Causes of the Wealth of Nations':
            year_pub.append(1776)
            continue

        elif author == 'Immanuel Kant':
            if title == 'The Critique of Pure Reason First Part':
                year_pub.append(1781)
                continue

            elif title == 'The Critique of Pure Reason Second Part':
                year_pub.append(1787)
                continue
            else:
                title = title

        elif author == 'John Stuart Mill':
            if title[:17] == 'A System of Logic':
                year_pub.append(1843)
                continue
            elif title == 'Liberty' or title == 'Utilitarianism' or title == 'The Subjection of Women':
                title = title
            else:
                year_pub.append(1873)
                continue

        for long_title in long_titles:
            if title in long_title:
                components = re.split(r'[(),]', long_title)
                for component in components:
                    year = filter(str.isdigit, component)
                    if len(year) >= 3:
                        year_pub.append(int(year[:4]))
                        break

    base_pdf_link = 'http://www.earlymoderntexts.com'

	# Get pdf links for each text
    links = [unidecode(x['href']) for x in soup.select('li a')][5:]
    first_pdf = links[0].split('/')[-1]

    pdf_links = [base_pdf_link + links[0]]
    filepaths = [os.path.expanduser('~') + '/philosophy_capstone/pdfs/' + first_pdf]

    last_doc = links[0]
    for link in links[1:]:
        if last_doc[:-4] in link:
            continue
        else:
            text_link = base_pdf_link + link
            pdf_name = link.split('/')[-1]
            filepaths.append(os.path.expanduser('~') + '/philosophy_capstone/pdfs/' + pdf_name)
            pdf_links.append(text_link)
            last_doc = link

    return text_author, titles, year_pub, pdf_links, filepaths

def download_pdfs(authors):
	'''
	Download pdfs of each author's texts
	'''
	documents = defaultdict(dict)
	for author in authors:
		# Get pdf
	    print('\nReceiving PDF\'s for {}'.format(author))
	    text_author, titles, year_pub, pdf_links, filepaths = get_pdfs(author)

		# Download all of the author's pdfs
	    for i in range(len(pdf_links)):
	        print('Downloading PDF {} for {}'.format(i, author))
	        urllib.urlretrieve(pdf_links[i], filepaths[i])
	        print('Adding Document')
	        documents = add_document(documents, text_author, titles[i], year_pub[i], pdf_links[i], filepaths[i])
	        time.sleep(5)

	return documents

def convert(fname, pages=None):
	'''
	Get text from pdf
	'''
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = file(fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close

    return text

'''
------ Original Python 2 function --------
def get_text(pdf_file, author):

	# Clean text received from convert function

    text = convert(pdf_file)

    start = text.find('Copyright')
    end = text[start:].find(author) + len(text[:start])

	# Check if the start and end worked.  If not, just scrape entire text
    if not (start == -1 or end == -1):
        text = text[:start] + text[end-1:]
        name_first = text.find(author)
        idx = name_first + len(author)
        text = text[:idx] + text[idx:].replace(author, '')

    text = text.strip(punctuation)

    if not(text.isalpha()):
        text_lst = text.split()

        for i in range(len(text_lst)):
            if not(text_lst[i].isalpha()):
                text_lst[i] = filter(str.isalnum, text_lst[i])

        text = ' '.join(word for word in text_lst)

    return text
'''

def convert(fname, pages=None):
	'''
	Get text from pdf (Python 3 version)
	'''
	fp = open(fname, 'rb')
	parser = PDFParser(fp)
	doc = PDFDocument()
	parser.set_document(doc)
	doc.set_parser(parser)
	doc.initialize('')
	rsrcmgr = PDFResourceManager()
	laparams = LAParams()
	device = PDFPageAggregator(rsrcmgr, laparams=laparams)
	interpreter = PDFPageInterpreter(rsrcmgr, device)
	# Process each page contained in the document.
	text = ''
	for page in doc.get_pages():
	    interpreter.process_page(page)
	    layout = device.get_result()
	    for lt_obj in layout:
	        if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
	            text += lt_obj.get_text()
	return text

def save_dfs(documents_dict, philosopher_dict):
	'''
	Save the dataframes for future use and add the text for each document
	'''
	lst = []
	for key in documents_dict.keys():
	    lst.append(documents[key])

	# Dataframe containing all the documents
	documents_df = pd.DataFrame(lst)
	documents_df['text'] = np.nan

	# Obtain text for all documents
	documents_df = scrape_pdfs(documents_df)

	phil_list = []
	for key in philosophers_dict.keys():
	    philosophers_dict[key]['name'] = key
	    phil_list.append(philosophers_dict[key])

	# Make philosophers dataframe
	philosophers_df = pd.DataFrame(phil_list)

	# Reorganize columns
	cols = list(philosophers_df)
	cols.insert(0, cols.pop(cols.index('name')))
	cols.insert(2, cols.pop(cols.index('time_period')))
	cols.insert(3, cols.pop(cols.index('year_born')))
	cols.insert(4, cols.pop(cols.index('year_died')))
	philosophers_df = philosophers_df.ix[:, cols]

	# Save dataframes in data folder
	documents_path = '~/philosophy_capstone/data/documents.csv'
	philosophers_path = '~/philosophy_capstone/data/philosophers.csv'

	documents_df.to_csv(documents_path)
	philosophers_df.to_csv(philosophers_path)

def scrape_pdfs(documents_df):
	# Obtain text for each document
	for i in range(documents_df.shape[0]):
	    author = documents_df.loc[i, 'author']
	    pdf_file = documents_df.loc[i, 'pdf_file']
	    documents_df.loc[i, 'text'] = get_text(pdf_file, author)
		print('Getting text from: {}'.format(documents_df.loc[i, 'title']))

	return documents_df

def main():
	philosophers = ppd.western_philosophers()
	philosophers, authors = add_to_philosophers_dict(philosophers)
	documents = download_pdfs(authors)
	save_dfs(documents, philosophers)
