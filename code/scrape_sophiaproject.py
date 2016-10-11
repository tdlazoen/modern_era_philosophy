from unidecode import unidecode
import urllib
from dataframes import Philosophers, Documents
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from string import punctuation
from cStringIO import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFTextExtractionNotAllowed
import time
import shutil
import os
import re

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

	for i in xrange(len(links)):
		link = links[i]
		title = titles[i]
		year = 0

		pdf_name = re.split(r'/', link)[-1]
		filepath = os.path.expanduser('~') + '/philosophy_capstone/pdfs/' + pdf_name

		if not os.path.isfile(filepath):
			print '\nDownloading pdf'
			urllib.urlretrieve(link, filepath)
		else:
			print '\nFile {} already exists!'.format(title)
			print 'Getting Text from {}'.format(title)
			text = get_text(filepath, 'cicero')
			print 'Adding Document'
			docs.add_document(author, title, year, text, link, filepath)

		time.sleep(10)

	return driver

def other_philosophers(phils, docs):
	url = 'http://www.sophia-project.org/classical-philosophy.html'

	driver = init_driver()

	driver.get(url)

	# philosophers = driver.find_elements_by_xpath('//*[@id="wsite-content"]/div/div/div/table/tbody/tr/td[1]/div/div/div/table/tbody/tr/td[1]/div[@class="paragraph"]')
	philosophers = driver.find_elements_by_xpath('//td[@class="wsite-multicol-col"][1]/div[@class="paragraph"]')
	authors = [unidecode(x.text).strip() for x in philosophers[:-1]]

	links_text = driver.find_elements_by_xpath('//div[@class="paragraph"]//a')
	links = [unidecode(x.get_attribute('href')).strip() for x in links_text]
	idx = links.index('http://www.sophia-project.org/nicomachean-ethics.html')
	titles = [unidecode(x.text).lower().strip() for x in links_text]
	titles = [re.split(r'[\[\]]', x)[0].strip() for x in titles]
	links.pop(idx)
	titles.pop(idx)
	authors.pop(idx)

	links = links[:-10]
	titles = titles[:-10]

	stockl = False
	martyr = False
	tertullian = False
	for i in xrange(len(links)):
		if authors[i] == 'albert stockl' and stockl == False:
			phils.add_philosopher_entry(authors[i], 1823, 1895)
			albert = True

		elif authors[i] == 'justin martyr' and martyr == False:
			phils.add_philosopher_entry(authors[i], 100, 165)
			martyr = True

		elif authors[i] == 'tertullian' and tertullian == False:
			phils.add_philosopher_entry(authors[i], 155, 240)

		elif authors[i] == 'seneca':
			authors[i] = 'seneca the younger'

		elif authors[i] == 'diogenes laerius':
			authors[i] = 'diogenes laertius'

		if authors[i].lower() in phils.df.name.values:
			if 'nicomachean ethics' in titles[i]:
				continue

			elif titles[i] not in docs.df.title.values:
				link = links[i]
				title = titles[i]
				author = authors[i]
				year = 0

				pdf_name = re.split(r'/', link)[-1]
				filepath = os.path.expanduser('~') + '/philosophy_capstone/pdfs/' + pdf_name

				if not os.path.isfile(filepath):
					print '\nDownloading pdf'
					urllib.urlretrieve(link, filepath)
					with open(filepath) as f:
						new_filepath = re.split(r'\.', filepath)[0] + '_.pdf'
						new_f = file(new_filepath, 'w')
						new_f.write(f.read())
						new_f.close()
					os.remove(filepath)
					filepath = new_filepath
				else:
					print '\nFile {} already exists!'.format(title)

				print 'Getting Text from {}'.format(title)
				text = get_text(filepath, authors[i])
				print 'Adding Document'
				docs.add_document(author, title, year, text, link, filepath)

				time.sleep(10)
			else:
				print '{} already exists!'.format(titles[i])


	return driver

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
	try:
		for page in PDFPage.get_pages(infile, pagenums):
			interpreter.process_page(page)
	except PDFTextExtractionNotAllowed:
		print 'This pdf won\'t allow text extraction!'

	infile.close()
	converter.close()
	text = output.getvalue()
	output.close

	return text

def get_text(pdf_file, author):
	'''
	Clean text received from convert function
	'''
	text = convert(pdf_file)

	text = text.strip(punctuation)

	if not(text.isalpha()):
		text_lst = text.split()

		for i in xrange(len(text_lst)):
			if not(text_lst[i].isalpha()):
				text_lst[i] = filter(str.isalnum, text_lst[i])

		text = ' '.join(word for word in text_lst)

	return text.lower()

if __name__ == '__main__':
	phils, docs = Philosophers(filepath='../data/philosophers.csv'), Documents(filepath='../data/documents.csv')
	# driver = cicero(docs)
	driver = other_philosophers(phils, docs)
