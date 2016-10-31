import numpy as np
import pandas as pd
import pickle
from modern_dfs import ModernPhilosophers, ModernDocuments
from spacy.en import English
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from nltk.corpus import stopwords
from spacy.en import English
from string import punctuation
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import pdb

def load_data():
    phils = ModernPhilosophers()
    docs = ModernDocuments()

    full_texts = docs.df['text'].values
    titles = docs.df['title'].values

    return phils, docs, full_texts, titles

def clean_document(text):
    STOPLIST = set(stopwords.words('english') + ["n't", "'s", "'m", "'", "'re"] + list(ENGLISH_STOP_WORDS))

    doc = parser(text)
    # Let's merge all of the proper entities
    for ent in doc.ents:
        ent.merge(ent.root.tag_, ent.text, ent.label_)
    print('HI')

    # Part's of speech to keep in the result
    pos_lst = ['ADJ', 'ADV', 'NOUN', 'PROPN', 'VERB']
    tokens = [token.lemma_.lower().replace(' ', '_') for token in doc if token.pos_ in pos_lst]

    return ' '.join(x.strip(punctuation).strip() for x in tokens if x not in STOPLIST)

if __name__ == '__main__':
    phils, docs, full_texts, titles = load_data()
    parser = English()

    small_texts = full_texts[:5]

    # cleaned_texts = np.array([''] * len(full_texts))

    # for i in range(len(full_texts)):
    #     cleaned_texts[i] = clean_document(full_texts[i])

    vectorizer = TfidfVectorizer(preprocessor=clean_document)
    tfidf_matrix = vectorizer.fit_transform(full_texts)

    # with open('vectorizer.pkl', 'w') as f:
    #     pickle.dump(vectorizer, f)
    # with open('data/tfidf.pkl', 'w') as f:
    #     pickle.dump(tfidf_matrix, f)
