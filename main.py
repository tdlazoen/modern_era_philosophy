import numpy as np
import pandas as pd
import pickle
from modern_dfs import ModernPhilosophers, ModernDocuments
from spacy.en import English
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from nltk.corpus import stopwords
from spacy.en import English
from string import punctuation
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.base import TransformerMixin
import re
import pdb
from autocorrect import spell
import enchant

'''
This file processes the text data and
puts it into a quantitative form which will be used
to perform topic modeling
'''

# Global variables
STOPLIST = set(stopwords.words('english') + ["n't", "'s", "'m", "'", "'re", "'ve"] + list(ENGLISH_STOP_WORDS))

d = enchant.Dict('en_US')

tokenized_words = []

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
    titles = docs.df['title'].values

    return phils, docs, full_texts, titles

class TextCleaner(TransformerMixin):
    '''
    A transformer that will is used to clean the text
    before vectorizing the documents
    '''

    def transform(self, X, **transform_params):
        '''
        INPUT:
            X - numpy array of texts
        OUTPUT:
            Cleaned numpy array of documents
        '''
        return clean_documents(X)

    def fit(self, X, y=None, **fit_params):
        return self

def clean_documents(text):
    '''
    INPUT:
        text - a single philosophical text
    OUTPUT:
        text that has been cleaned based of unnecessary
        parts of speech, punctuation, and extra spaces

    Cleans a single document's text
    '''
    doc = parser(text)

    # Let's merge all of the proper entities
    for ent in doc.ents:
        ent.merge(ent.root.tag_, ent.text, ent.label_)

    # Part's of speech to keep in the result
    pos_lst = ['ADJ', 'ADV', 'NOUN', 'PROPN', 'VERB']
    tokens = [token.lemma_.lower().replace(' ', '_') for token in doc if token.pos_ in pos_lst]

    tokens = [token if d.check(token) else spell(token) for token in tokens if token not in STOPLIST]

    spaces_lst = ['', ' ', '\n', '\n\n', '\r'] + ' '.join(punctuation).split()
    tokens = [token.strip(punctuation).strip() for token in tokens if token not in spaces_lst]

    tokenized_words.append(tokens)

    return ' '.join(tokens)

if __name__ == '__main__':
    phils, docs, full_texts, titles = load_data()
    parser = English()

    # with open('vectorizer.pkl', 'w') as f:
    #     pickle.dump(vectorizer, f)
    # with open('data/tfidf.pkl', 'w') as f:
    #     pickle.dump(tfidf_matrix, f)
