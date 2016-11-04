from selenium import webdriver
from modern_dfs import ModernPhilosophers, ModernDocuments
from default_ordered_dict import DefaultOrderedDict
import json
import time
from autocorrect import spell
import enchant
from internetarchive import get_item, download
from string import punctuation
from requests.exceptions import ConnectionError
import pdb
import os
import codecs

def init_driver():
    driver = webdriver.Chrome()

    return driver

def scope_out_archives(phils, identifiers):
    driver = init_driver()
    driver.get('https://archive.org/details/texts?and[]=languageSorter%3A%22English%22&and[]=mediatype%3A%22texts%22')

    time.sleep(5)

    for i in range(77, phils.df.shape[0]):
        author = phils.df.loc[i, 'name']
        box = driver.find_element_by_xpath('//*[@id="tabby-collection"]/div/div[1]/form/input[1]')
        box.clear()
        box.send_keys('creator:' + author)
        box.submit()

        ident = input("Type identifier to add for {}: ".format(author))
        while ident != 'stop':
            identifiers.append((author, ident))
            ident = input("Type identifier to add for {}: ".format(author))

    return identifiers

def save_in_json(idents):
    pdb.set_trace()
    if isinstance(idents, list):
        ident_dict = DefaultOrderedDict(list)

        for name, identifier in idents:
            ident_dict[name].append(identifier)

        ident_dict = dict(ident_dict)

        if os.path.isfile('../data/identifers.json'):
            os.system('rm ../data/identifers.json')
        with open('../data/identifiers.json', 'w') as f:
            json.dump(ident_dict, f)
    else:
        if os.path.isfile('../data/identifers.json'):
            os.system('rm ../data/identifers.json')
        with open('../data/identifiers.json', 'w') as f:
            json.dump(idents, f)

def load_data(filename):
    with open(filename, 'r') as f:
        data = json.load(f)

    return data

def get_text(item, title):
    user = os.path.expanduser('~')

    text_file = [x['name'] for x in item.item_metadata['files'] if ('.txt' in x['name']) and ('meta.' not in x['name'])]

    text_file = text_file[0]

    new_filepath = user + '/philosophy_capstone/text_files/' \
                   + title.replace(' ', '_')

    item.get_file(text_file).download(new_filepath)

    with codecs.open(new_filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    return text, new_filepath

def clean_text(text):
    remove_begin_sections = ['PREFACE', 'INTRODUCTION', "NOTE", 'FOREWORD']
    remove_end_sections = ['INDEX', 'APPENDIX']
    d_us = enchant.Dict('en_US')
    d_gb = enchant.Dict('en_GB')

    text = text.replace('\n', '').replace('\r', '')

    for section in remove_begin_sections:
        idx = text.find(section)
        while idx > -1:
            if idx < 0.5 * len(text):
                text = text[idx + len(section):]
                idx = text.find(section)
            else:
                idx = -1
    for section in remove_end_sections:
        idx = text.find(section)
        if idx > -1 and idx > 0.5 * len(text):
            text = text[:idx]

    return text

def get_doc_info(ident_dict):
    driver = init_driver()
    driver.get('https://www.google.com')
    doc_info_dict = load_data('../data/ia_document_info.json')

    authors = doc_info_dict['authors']
    titles = doc_info_dict['titles']
    years = doc_info_dict['years']
    urls = doc_info_dict['urls']
    idents = doc_info_dict['identifiers']

    num_authors = len(authors)

    i = 0
    for author, identifiers in ident_dict.items():
        for ident in identifiers:
            url = 'https://archive.org/details/' + ident
            if i < num_authors:
                if url in urls:
                    i += 1
                continue

            item = get_item(ident)

            if 'metadata' in item.item_metadata:
                metadata = item.item_metadata['metadata']
            else:
                continue

            if isinstance(metadata['title'], list):
                title = metadata['title'][0].lower()
            else:
                title = metadata['title'].lower()
            if 'year' in metadata:
                if isinstance(metadata['year'], list):
                    year = int(metadata['year'][0])
                else:
                    year = int(metadata['year'])
            else:
                year = 0

            desired_title = input('\nIs the title "{}" by "{}" okay? '.format(title, author))

            if desired_title == 'n':
                title = input("What would you like the title to be? ").lower()
                print('The title is now "{}"'.format(title))
            elif desired_title == 'drop':
                continue

            box = driver.find_element_by_name('q')

            box.clear()
            box.send_keys(title + ' ' + author + ' year')
            box.submit()

            correct_year = input('\nIs {} the correct year? '.format(year))

            if correct_year == 'drop':
                continue
            elif not (correct_year == 'y'):
                year = int(input('\nWhat should the year be? '))
                print('The year has been set to {}'.format(year))

            doc_info_dict['authors'].append(author)
            doc_info_dict['titles'].append(title)
            doc_info_dict['years'].append(year)
            doc_info_dict['urls'].append(url)
            doc_info_dict['identifiers'].append(ident)

            with open('../data/ia_document_info.json', 'w') as f:
                json.dump(doc_info_dict, f)

    driver.quit()
    return authors, titles, urls, years, idents

def add_documents(docs, docs_info):
    authors = docs_info['authors']
    titles = docs_info['titles']
    years = docs_info['years']
    urls = docs_info['urls']
    idents = docs_info['identifiers']

    for i in range(len(authors)):
        author = authors[i].strip()
        title = titles[i].strip()
        year = years[i]
        url = urls[i].strip()
        ident = idents[i].strip()

        item = get_item(ident)

        print('\nGetting text for {}'.format(title))
        text, filepath = get_text(item, title)

        print('Cleaning text')
        text = clean_text(text)

        print(len(text.split()))
        if len(text.split()) < 1000:
            cont = input("continue? ")
            if cont == 'n':
                break
        if title in docs.df.title.values:
            print('Another part of {} already exists! Adding text now'.format(title))
            idx = docs.df[docs.df.title == title].index
            docs.df.loc[idx, 'text'] += text
        else:
            print('Adding document {}'.format(title))
            docs.add_document(author, title, year, text, url, filepath)

if __name__ == '__main__':
    phils, docs = ModernPhilosophers(), ModernDocuments()
    # identifiers = scope_out_archives(phils)
    # save_in_json(identifiers)

    # ident_dict = load_data('../data/identifiers.json')

    # authors, titles, urls, years, idents = get_doc_info(ident_dict)

    docs_info = load_data('../data/ia_document_info.json')
    add_documents(docs, docs_info)
