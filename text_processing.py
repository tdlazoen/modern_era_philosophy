import numpy as np
import pandas as pd
import pickle
from modern_dfs import ModernPhilosophers, ModernDocuments
from spacy.en import English
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from nltk.corpus import stopwords
from spacy.en import English
from string import punctuation
import multiprocessing
import re
import pdb
from collections import Counter


'''
This file processes the text data and
puts it into a quantitative form which will be used
to perform topic modeling
'''


# Global variables
STOPLIST = set(stopwords.words('english') + ["n't", "'s", "'m", "'", "'re", "'ve"] \
           + ['philosophy', 'philosophers'] + list(ENGLISH_STOP_WORDS)) + \
           list([ch for ch in 'abcdefghijklmnopqrstuvwxyz'])


def clean_document(doc):
    '''
    INPUT:
        text - a single philosophical text
    OUTPUT:
        text that has been cleaned based of unnecessary
        parts of speech, punctuation, and extra spaces

    Cleans a single document's text
    '''
    # Part's of speech to keep in the result
    pos_lst = ['ADJ', 'ADV', 'NOUN', 'PROPN', 'VERB', 'AUX']
    tokens = [token.lemma_.lower().strip(punctuation).strip().replace(' ', '_') for token in doc if token.pos_ in pos_lst]

    spaces_lst = ['', ' ', '\n', '\n\n', '\r']
    tokens = [token for token in tokens if token not in spaces_lst]

    tokens = [token for token in tokens if token not in STOPLIST]

    clean_text = ' '.join(token for token in tokens)

    return clean_text, tokens


def cleanse_corpus(documents):
    '''
    INPUT:
        documents - an array-like object of text documents
    OUTPUT:
        cleaned_texts - an array of documents cleaned of
                        unnecessary words and characters
        parsed_docs - an array containing the parsed SpaCy
                      doc objects

    Cleanses entire corpus of documents using SpaCy
    '''
    parsed_docs = []
    tokenized_docs = []

    num_cores = multiprocessing.cpu_count()
    batch_size = min(int(len(documents) / (num_cores * 2)), 20)
    if batch_size == 0:
        batch_size = 1

    print("{} Documents Total with {} Cores Working".format(len(documents), num_cores-1))
    num_doc = 1
    for doc in parser.pipe(documents, batch_size=batch_size, n_threads=num_cores - 1):
        print("\nCleaning Text for Document {}".format(num_doc))
        cleaned_text, tokens = clean_document(doc)
        doc = parser(cleaned_text)
        parsed_docs.append(doc)
        tokenized_docs.append(tokens)
        num_doc += 1

    return parsed_docs, tokenized_docs


def load_data():
    '''
    INPUT:
        None
    OUTPUT:
        phils - Dataframe of philosopher data
        docs - Dataframe of document data
        full_texts - Complete text of each document in docs
        titles - Titles of each document in doc

    Load in the philosopher and document data
    and return useful information for topic modeling
    '''
    phils = ModernPhilosophers()
    docs = ModernDocuments()

    full_texts = docs.df['text'].values

    return phils, docs, full_texts


if __name__ == '__main__':
    phils, docs, full_texts = load_data()
    print('Downloading Parser...')
    parser = English()

    parsed_docs, tokenized_docs = cleanse_corpus(full_texts)
    print('Finished!  Beginning Next Process...')

    print('\nPickling objects...')
    with open('data/model/tokenized_docs.pkl', 'wb') as f:
        pickle.dump(tokenized_docs, f)
    with open('data/model/parsed_docs.pkl', 'wb') as f:
        pickle.dump(parsed_docs, f)
