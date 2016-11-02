from selenium import webdriver
from modern_dfs import ModernPhilosophers, ModernDocuments
from default_ordered_dict import DefaultOrderedDict
import json
import time
from autocorrect import spell
import enchant
from internetarchive import get_item, download
import pdb

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

def save_in_json(identifiers):
    ident_dict = DefaultOrderedDict(list)

    for name, identifier in identifiers:
        ident_dict[name].append(identifier)

    ident_dict = dict(ident_dict)

    with open('../data/identifiers.json', 'w') as f:
        json.dump(ident_dict, f)

def load_data(filename):
    with open(filename, 'r') as f:
        identifiers = json.load(f)

    return identifiers

def get_text(item):
    return

def clean_text(text):
    return

def add_documents(docs, ident_dict):
    for author, identifiers in ident_dict.items():
        for ident in identifiers:
            item = get_item(ident)
            metadata = item.item_metadata['metadata']
            title = metadata['title']
            if 'year' in metadata:
                year = int(metadata['year'])
            else:
                year = 0
            url = metadata['identifier-access']

            desired_title = input('\nIs the title "{}" by "{}" okay? '.format(title, author))

            if not (desired_title == 'y'):
                title = input("What would you like the title to be? ")
                print('The title is now "{}"'.format(title))

            correct_year = input('\nIs {} the correct year? '.format(year))

            if not (correct_year == 'y'):
                year = int(input('\nWhat should the year be? '))
                print('The year has been set to {}'.format(year))

            # text, filepath = get_text(item)
            # text = clean_text(text)


if __name__ == '__main__':
    phils, docs = ModernPhilosophers(), ModernDocuments()
    # identifiers = scope_out_archives(phils)
    # save_in_json(identifiers)

    ident_dict = load_data('../data/identifiers.json')

    add_documents(docs, ident_dict)
