import numpy as np
import pandas as pd
from modern_dfs import ModernPhilosophers, ModernDocuments
from spacy.en import English
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from nltk.corpus import stopwords
from spacy.en import English
from string import punctuation
import re

def load_data():
    phils = ModernPhilosophers()
    docs = ModernDocuments()

    full_texts = docs.df['text'].values
    titles = docs.df['title'].values

    return phils, docs, full_texts, titles

def clean_document(text):
    STOPLIST = set(stopwords.words('english') + ["n't", "'s", "'m", "'", "'re"] + list(ENGLISH_STOP_WORDS))

    PUNCT_DICT = {ord(punc): None for punc in punctuation if punc not in ['_', '*']}

    doc = parser(text)
    # Let's merge all of the proper entities
    for ent in doc.ents:
        ent.merge(ent.root.tag_, ent.text, ent.label_)
    print('HI')

    # Part's of speech to keep in the result
    pos_lst = ['ADJ', 'ADV', 'NOUN', 'PROPN', 'VERB']
    tokens = [token.lemma_.lower().replace(' ', '_') for token in doc]# if token.pos_ in pos_lst]

    return ' '.join(token for token in tokens if token not in STOPLIST)

if __name__ == '__main__':
    phils, docs, full_texts, titles = load_data()
    parser = English()

    small_texts = full_texts[:5]

    cleaned_texts = np.array([''] * len(small_texts))

    for i in range(len(small_texts)):
        cleaned_texts[i] = clean_document(small_texts[i])
