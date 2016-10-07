import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from default_ordered_dict import DefaultOrderedDict
from itertools import izip
from string import punctuation
import urllib
import os
import re

# Add a document to the dictionary
def add_document(dct, idx, author, work_title, link):
    dct[str(idx)]['author'] = author
    dct[str(idx)]['work_title'] = work_title
	dct[str(idx)]['url'] = link

    return dct

def work_titles(title_links):
	# Initialize work title variables
    work_titles = []
    work_mask = [] # Used for creating authors list later
    tpt_part = 1

    # Initialize link variables
    cleaned_links = []

    # Run through each title and link in the list
    for i, entry in enumerate(titles_links[1:]):
        try:
            # Get text associated with entry (title of work)
            x = unidecode(entry.string)
            x = re.split(r'[()]', x)[0]

            # Get link associated with entry
            link = 'https:' + unidecode(entry['href']).strip('/')

            # Used for inconsistencies
            if x == 'vol. 1' and i == 48:
                work_titles.append('A System Of Logic, Ratiocinative And Inductive, 3rd ed. ' + x.strip())

                # Add link information for the work
                cleaned_links.append(link)

            elif x == 'vol. 2' or i == 49:
                work_titles.append('A System Of Logic, Ratiocinative And Inductive, 7th ed. ' + x.strip())

                # Add link information for the work
                cleaned_links.append(link)

            elif x == '8th ed.':
                work_titles.append('A System Of Logic, Ratiocinative And Inductive ' + x.strip())

                # Add link information for the work
                cleaned_links.append(link)

            elif i in range(105, 109):
                work_title = 'Theologico-Political Treatise -- ' + 'part ' + str(tpt_part)
                work_titles.append(work_title)
                tpt_part += 1

                # Add link information for the work
                cleaned_links.append(link)

            elif x == 'Butcher trans.' or x == 'audio' or x == 'audiobook' or x[:4] == 'part':
                continue

            else:
                # Append title to the list of work titles
                work_titles.append(x.strip())
                work_mask.append(x.strip())

                # Add link information for the work
                cleaned_links.append(link)

        # Check for possible links that aren't for philosophical works
        except AttributeError:
            continue

	return work_titles, work_mask, cleaned_links

# Obtain documents from the gutenberg project website
def gutenberg_works_and_authors():
    '''
    Creates and returns work titles with corresponding links and authors
    '''
    # Base url for retrieving information
    url = 'https://www.gutenberg.org/wiki/Philosophy_(Bookshelf)'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    # Obtain titles of works and links to each work
    titles_links = soup.select('a.extiw')

    # Initialize work title variables
    work_titles = []
    work_mask = [] # Used for creating authors list later
    tpt_part = 1

    # Initialize link variables
    cleaned_links = []

    # Run through each title and link in the list
    # for i, entry in enumerate(titles_links[1:]):
    #     try:
    #         # Get text associated with entry (title of work)
    #         x = unidecode(entry.string)
    #         x = re.split(r'[()]', x)[0]
	#
    #         # Get link associated with entry
    #         link = 'https:' + unidecode(entry['href']).strip('/')
	#
    #         # Used for inconsistencies
    #         if x == 'vol. 1' and i == 48:
    #             work_titles.append('A System Of Logic, Ratiocinative And Inductive, 3rd ed. ' + x.strip())
	#
    #             # Add link information for the work
    #             cleaned_links.append(link)
	#
    #         elif x == 'vol. 2' or i == 49:
    #             work_titles.append('A System Of Logic, Ratiocinative And Inductive, 7th ed. ' + x.strip())
	#
    #             # Add link information for the work
    #             cleaned_links.append(link)
	#
    #         elif x == '8th ed.':
    #             work_titles.append('A System Of Logic, Ratiocinative And Inductive ' + x.strip())
	#
    #             # Add link information for the work
    #             cleaned_links.append(link)
	#
    #         elif i in range(105, 109):
    #             work_title = 'Theologico-Political Treatise -- ' + 'part ' + str(tpt_part)
    #             work_titles.append(work_title)
    #             tpt_part += 1
	#
    #             # Add link information for the work
    #             cleaned_links.append(link)
	#
    #         elif x == 'Butcher trans.' or x == 'audio' or x == 'audiobook' or x[:4] == 'part':
    #             continue
	#
    #         else:
    #             # Append title to the list of work titles
    #             work_titles.append(x.strip())
    #             work_mask.append(x.strip())
	#
    #             # Add link information for the work
    #             cleaned_links.append(link)
	#
    #     # Check for possible links that aren't for philosophical works
    #     except AttributeError:
    #         continue

	work_titles, work_maks, links = work_titles(title_links)

    # Drop idx of item in order to prevent doubles
    drop_idx = []
    drop_idx.append(work_titles.index('A System Of Logic, Ratiocinative And Inductive, 3rd ed. vol. 1'))

    # Get the names associated with each work
    names = soup.select('li')

    # Get the cleaned names list
    authors_and_works = [unidecode(x.get_text()).strip() for x in names[15:126]]
    authors_and_works = [re.split(r'[()]', name)[0].strip() for i, name in enumerate(authors_and_works) if i not in drop_idx]
    authors_and_works.remove('Benedictus de Spinoza Theologico-Political Treatise -- Part 1')

    # Loop through list of author names (with books attached) and get only author names
    authors = []
    for i in xrange(len(authors_and_works)):
        name = authors_and_works[i].replace(work_mask[i], '').strip()
        authors.append(name)

    # Insert authors for books where need be (i.e. multiple volumes or parts)
    for i in xrange(len(work_titles)):

        # Multiple edition/volumes of below work
        if work_titles[i][:46] == 'A System Of Logic, Ratiocinative And Inductive':
            authors.insert(i, 'John Stuart Mill')

        # 4-part Theologico-Political Treatise
        elif '--' in work_titles[i]:
            authors.insert(i, 'Benedictus de Spinoza')

    # Account for duplicate works
    for work in work_title:
        if work_title.count(work) >= 2:
            idx = work_title.index(work)
            authors.pop(idx)
            work_titles.pop(idx)
            links.pop(idx)

    return authors, work_titles, links

def get_document_text(url):
	unique_id = filter(str.isdigit, url)
	doc_url = 'https://www.gutenberg.org/files/{}/{}-h/{}-h.htm'.format(unique_id, unique_id, unique_id)
	r = requests.get(doc_url)
	soup = BeautifulSoup(r.content, 'html.parser')
	pars = soup.select('p')

	paragraphs = []
    for i in xrange(len(pars)):
        try:
            cl = unidecode(pars[i]['class'][0])
            if cl == 'toc' or pars[i] == '':
                continue
            else:
                text = unidecode(pars[i].get_text().strip())
                paragraphs.append(text.replace('\r\n', '').strip())
        except KeyError:
            text = unidecode(pars[i].get_text())
            paragraphs.append(text.replace('\r\n', '').strip())

	paragraphs = [paragraph for paragraph in paragraphs if len(paragraph) >= 10]

	text = None

	for paragraph in paragraphs:
		paragraph_words = paragraph.strip.split()
		text += ' '.join([word for word in paragraph_words])

	return text

def gutenberg_docs():
	documents = DefaultOrderedDict(dict)
	authors, work_titles, urls = gutenberg_works_and_authors()

	for i in xrange(len(authors)):
		documents = add_document(documents, i, authors[i], work_titles[i], urls[i])
		documents[i]['doc_text'] = get_document_text(urls[i])

	return documents

if __name__ == '__main__':
	gut_docs = gutenberg_docs()
