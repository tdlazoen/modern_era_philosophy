import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from default_ordered_dict import DefaultOrderedDict
from itertools import izip
from string import punctuation
import urllib
import os
import re
import time

# Add a document to the dictionary
def add_document(dct, idx, author, doc_title, link):
	dct[str(idx)]['author'] = author
	dct[str(idx)]['document_title'] = doc_title
	dct[str(idx)]['url'] = link

	return dct

# def get_document_info(tags):
# 	# Initialize document title variables
# 	doc_titles = []
# 	doc_mask = [] # Used for creating authors list later
# 	tpt_part = 1
#
# 	# Initialize link variables
# 	cleaned_links = []
#
# 	# Run through each title and link in the list
# 	for i, entry in enumerate(tags[1:]):
# 		try:
# 			# Get text associated with entry (title of document)
# 			x = unidecode(entry.string)
# 			x = re.split(r'[()]', x)[0]
#
# 			# Get link associated with entry
# 			link = 'https:' + unidecode(entry['href']).strip('/')
#
# 			# Used for inconsistencies
# 			if x == 'vol. 1' and i == 48:
# 				doc_titles.append('A System Of Logic, Ratiocinative And Inductive, 3rd ed. ' + x.strip())
#
# 				# Add link information for the document
# 				cleaned_links.append(link)
#
# 			elif x == 'vol. 2' or i == 49:
# 				doc_titles.append('A System Of Logic, Ratiocinative And Inductive, 7th ed. ' + x.strip())
#
# 				# Add link information for the document
# 				cleaned_links.append(link)
#
# 			elif x == '8th ed.':
# 				doc_titles.append('A System Of Logic, Ratiocinative And Inductive ' + x.strip())
#
# 				# Add link information for the document
# 				cleaned_links.append(link)
#
# 			elif i in range(105, 109):
# 				doc_title = 'Theologico-Political Treatise -- ' + 'part ' + str(tpt_part)
# 				doc_titles.append(doc_title)
# 				tpt_part += 1
#
# 				# Add link information for the document
# 				cleaned_links.append(link)
#
# 			elif x == 'Butcher trans.' or x == 'audio' or x == 'audiobook' or x[:4] == 'part':
# 				continue
#
# 			else:
# 				# Append title to the list of document titles
# 				doc_titles.append(x.strip())
# 				doc_mask.append(x.strip())
#
# 				# Add link information for the document
# 				cleaned_links.append(link)
#
# 		# Check for possible links that aren't for philosophical documents
# 		except AttributeError:
# 			continue
#
# 	return doc_titles, doc_mask, cleaned_links
#
# # Obtain documents from the gutenberg project website
# def gutenberg_info():
# 	'''
# 	Creates and returns work titles with corresponding links and authors
# 	'''
# 	# Base url for retrieving information
# 	url = 'https://www.gutenberg.org/wiki/Philosophy_(Bookshelf)'
# 	time.sleep(5)
# 	r = requests.get(url)
# 	soup = BeautifulSoup(r.content, 'html.parser')
#
# 	# Obtain titles of documents and links to each one
# 	titles_links = soup.select('a.extiw')
#
# 	doc_titles, doc_mask, links = get_document_info(titles_links)
#
# 	# Drop idx of item in order to prevent doubles
# 	drop_idx = []
# 	drop_idx.append(doc_titles.index('A System Of Logic, Ratiocinative And Inductive, 3rd ed. vol. 1'))
#
# 	# Get the names associated with each document
# 	names = soup.select('li')
#
# 	# Get the cleaned names list
# 	authors_and_docs = [unidecode(x.get_text()).strip() for x in names[15:126]]
# 	authors_and_docs = [re.split(r'[()]', name)[0].strip() for i, name in enumerate(authors_and_docs) if i not in drop_idx]
# 	authors_and_docs.remove('Benedictus de Spinoza Theologico-Political Treatise -- Part 1')
#
# 	# Loop through list of author names (with books attached) and get only author names
# 	authors = []
# 	for i in xrange(len(authors_and_docs)):
# 		name = authors_and_docs[i].replace(doc_mask[i], '').strip()
# 		authors.append(name)
#
# 	# Insert authors for books where need be (i.e. multiple volumes or parts)
# 	for i in xrange(len(doc_titles)):
# 		# Multiple edition/volumes of below work
# 		if doc_titles[i][:46] == 'A System Of Logic, Ratiocinative And Inductive':
# 			authors.insert(i, 'John Stuart Mill')
#
# 		# 4-part Theologico-Political Treatise
# 		elif '--' in doc_titles[i]:
# 			authors.insert(i, 'Benedictus de Spinoza')
#
# 	# Account for duplicate documents
# 	for doc in doc_titles:
# 		if doc_titles.count(doc) >= 2:
# 			idx = doc_titles.index(doc)
# 			authors.pop(idx)
# 			doc_titles.pop(idx)
# 			links.pop(idx)
#
# 	return authors, doc_titles, links
#
# def get_document_text(url):
# 	unique_id = filter(str.isdigit, url)
# 	time.sleep(5)
# 	doc_url = 'https://www.gutenberg.org/files/{}/{}-h/{}-h.htm'.format(unique_id, unique_id, unique_id)
# 	r = requests.get(doc_url)
# 	soup = BeautifulSoup(r.content, 'html.parser')
# 	pars = soup.select('p')
#
# 	paragraphs = []
# 	for i in xrange(len(pars)):
# 		try:
# 			cl = unidecode(pars[i]['class'][0])
# 			if cl == 'toc' or pars[i] == '':
# 				continue
# 			else:
# 				text = unidecode(pars[i].get_text().strip())
# 				paragraphs.append(text.replace('\r\n', '').strip())
# 		except KeyError:
# 			text = unidecode(pars[i].get_text())
# 			paragraphs.append(text.replace('\r\n', '').strip())
#
# 	paragraphs = [paragraph for paragraph in paragraphs if len(paragraph) >= 10]
#
# 	text = ''
#
# 	for paragraph in paragraphs:
# 		paragraph_words = paragraph.strip().split()
# 		text += ' '.join([word for word in paragraph_words])
#
# 	return text
#
# def gutenberg_docs():
# 	documents = DefaultOrderedDict(dict)
# 	authors, doc_titles, urls = gutenberg_info()
#
# 	for i in xrange(len(authors)):
# 		print '\nAdding document {} to Dictionary'.format(doc_titles[i])
# 		documents = add_document(documents, i, authors[i], doc_titles[i], urls[i])
# 		print 'Retrieving Document text for document {}'.format(doc_titles[i])
# 		documents[i]['doc_text'] = get_document_text(urls[i])
# 		print documents[i]['doc_text'][:5]
#
# 	return documents



if __name__ == '__main__':
	# gut_docs = gutenberg_docs()
