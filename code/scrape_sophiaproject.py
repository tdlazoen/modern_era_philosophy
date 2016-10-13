from unidecode import unidecode
import urllib
from dataframes import Philosophers, Documents
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from string import punctuation
from io import StringIO
'''
------- Originally used for python 2 ------------
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFTextExtractionNotAllowed
'''
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
import time
import os
import re

'''
This file scrapes the the sophia-project site for additional documents
http://www.sophia-project.org/classical-philosophy.html
'''

def init_driver():
	driver = webdriver.Chrome()
	driver.implicitly_wait(10)
	driver.wait = WebDriverWait(driver, 10)

	return driver

def cicero(docs):
	url = 'http://www.sophia-project.org/classical-philosophy.html'

	driver = init_driver()

	driver.get(url)

	cicero_links = driver.find_elements_by_xpath('//*[@id="wsite-content"]/div/div/div/table/tbody/tr/td[1]/div[19]/div/div/table/tbody/tr/td[2]/div[position() < 8]/a')

	links = [unidecode(x.get_attribute('href')).strip() for x in cicero_links]

	author = 'marcus tullius cicero'
	titles = [unidecode(re.split(r'[\[\]]', x.text)[0]).lower().strip() for x in cicero_links]

	for i in range(len(links)):
		link = links[i]
		title = titles[i]
		year = 0

		pdf_name = re.split(r'/', link)[-1]
		filepath = os.path.expanduser('~') + '/philosophy_capstone/pdfs/' + pdf_name

		if not os.path.isfile(filepath):
			print('\nDownloading pdf')
			urllib.urlretrieve(link, filepath)
		else:
			print('\nFile {} already exists!'.format(title))
			print('Getting Text from {}'.format(title))
			text = get_text(filepath, 'cicero')
			print('Adding Document')
			docs.add_document(author, title, year, text, link, filepath)

		time.sleep(10)

	return driver

def other_philosophers(phils, docs):
	url = 'http://www.sophia-project.org/classical-philosophy.html'

	driver = init_driver()

	driver.get(url)

	philosophers = driver.find_elements_by_xpath('//td[@class="wsite-multicol-col"][1]/div[@class="paragraph"]')
	authors = [unidecode(x.text).lower().strip() for x in philosophers][:-1]
	authors = authors[1:]
	idx_sandbach = authors.index('f.h. sandbach')
	authors.pop(idx_sandbach)

	links_text = driver.find_elements_by_xpath('//div[@class="paragraph"]//a')
	links = [unidecode(x.get_attribute('href')).strip() for x in links_text][:-10]
	idx_russo_ethics = links.index('http://www.sophia-project.org/uploads/1/3/9/5/13955288/russo_stoicism_ethics.pdf')
	links.pop(idx_russo_ethics)
	idx_zeno = links.index('http://www.sophia-project.org/uploads/1/3/9/5/13955288/sandbach_zeno.pdf')
	links.pop(idx_zeno)
	idx_plato_study = links.index('http://www.sophia-project.org/apology.html')
	links.pop(idx_plato_study)

	titles = [unidecode(x.text).lower().strip() for x in links_text][:-10]
	titles = [x for x in titles if not (x == '')]
	titles.pop(idx_zeno)
	titles.pop(idx_plato_study)

	idx1 = links.index('http://www.sophia-project.org/nicomachean-ethics.html')
	links.pop(idx1)
	titles.pop(idx1)
	authors.pop(idx1)

	idx2 = authors.index('socrates')
	authors.pop(idx2)

	stockl = False
	martyr = False
	tertullian = False
	for i in range(len(links) - 10, len(links)):
		if authors[i] == 'albert stockl' and stockl == False:
			phils.add_philosopher_entry(authors[i], 1823, 1895)
			stockl = True

		elif authors[i] == 'justin martyr' and martyr == False:
			phils.add_philosopher_entry(authors[i], 100, 165)
			martyr = True

		elif authors[i] == 'tertullian' and tertullian == False:
			phils.add_philosopher_entry(authors[i], 155, 240)
			tertullian = True

		elif authors[i] == 'seneca':
			authors[i] = 'seneca the younger'

		elif authors[i] == 'diogenes laerius':
			authors[i] = 'diogenes laertius'

		elif authors[i] == 'lucian of samosata':
			phils.add_philosopher_entry(authors[i], 125, 180)

		elif authors[i] == 'pericles':
			phils.add_philosopher_entry(authors[i], -495, -429)

		elif authors[i] == 'quintilian':
			phils.add_philosopher_entry(authors[i], 35, 100)

		elif authors[i] == 'cicero':
			continue

		if authors[i].lower() in phils.df.name.values:
			if 'nicomachean ethics' in titles[i]:
				continue

			elif titles[i] not in docs.df.title.values:
				link = links[i]
				title = re.split(r'[\[\]]', titles[i])[0].strip()
				author = authors[i]
				year = 0

				pdf_name = re.split(r'/', link)[-1]
				filepath = os.path.expanduser('~') + '/philosophy_capstone/pdfs/' + pdf_name

				if not os.path.isfile(filepath):
					new_filepath = re.split(r'\.', filepath)[0] + '_new.pdf'
					if not os.path.isfile(new_filepath):
						print('\nDownloading pdf {}'.format(title))
						urllib.urlretrieve(link, filepath)
						os.system('qpdf --password="" --decrypt ' + filepath +' ' + new_filepath)
						os.remove(filepath)
						time.sleep(10)
					else:
						print('\nFile {} already exists!'.format(title))

					filepath = new_filepath

				else:
					print('\nFile {} already exists!'.format(title))


				print('Getting Text from {} by {}'.format(title, author))
				text = get_text(filepath, author)

				print('Adding Document')
				docs.add_document(author, title, year, text, link, filepath)

			else:
				print('{} already exists!'.format(titles[i]))


	return driver

def convert(fname, pages=None):
	'''
	Get text from pdf
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

def get_text(pdf_file, author):
	'''
	Clean text received from convert function
	'''
	text = convert(pdf_file)

	text = text.lower().strip(punctuation)

	text = text.replace('tetullian', 'tertullian')

	try:
		last_period = [m.start() for m in re.finditer(r'\.', text)][-11]

	except IndexError:
		last_period = -1

	text = text[:last_period]
	text = text.replace(author, '')
	text = text.replace('sophiaomni', '')
	text = text.replace('wwwsophiaomniorg', '')

	if not(text.isalpha()):
		text_lst = text.split()

		for i in range(len(text_lst)):
			if not(text_lst[i].isalpha()):
				text_lst[i] = filter(str.isalnum, text_lst[i])

		text = ' '.join(word for word in text_lst)

	return text

if __name__ == '__main__':
	phils, docs = Philosophers(filepath='../data/philosophers.csv'), Documents(filepath='../data/documents.csv')
	# driver = cicero(docs)
	# driver = other_philosophers(phils, docs)
