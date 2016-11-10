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
    pos_lst = ['NOUN']
    tokens = [token.lemma_.lower().strip(punctuation).strip().replace(' ', '_') for token in doc if token.pos_ in pos_lst]

    spaces_lst = ['', ' ', '\n', '\n\n', '\r']
    tokens = [token for token in tokens if token not in spaces_lst]

    tokens = [token for token in tokens if token not in STOPLIST]

    clean_text = ' '.join(token for token in tokens)
    return clean_text, tokens


def split_text(doc, title, n_words):
    words = str(doc).split()
    chunks = []
    current_chunk_words = []
    current_chunk_word_count = 0
    for word in words:
        current_chunk_words.append(word)
        current_chunk_word_count += 1
        if current_chunk_word_count == n_words:
            chunks.append(' '.join(current_chunk_words))
            current_chunk_words = []
            current_chunk_word_count = 0
    chunks.append(' '.join(current_chunk_words))

    return chunks, [title] * len(chunks)


def cleanse_corpus(documents, docs):
    '''
    INPUT:
        documents - an array-like object of text documents
        docs - documents dataframe
    OUTPUT:
        cleaned_texts - an array of documents cleaned of
                        unnecessary words and characters
        parsed_docs - an array containing the parsed SpaCy
                      doc objects

    Cleanses entire corpus of documents using SpaCy
    '''
    titles_chunks = []
    tokenized_docs = []

    num_cores = multiprocessing.cpu_count()
    batch_size = min(int(len(documents) / (num_cores * 2)), 20)
    if batch_size == 0:
        batch_size = 1

    print("{} Documents Total with {} Cores Working".format(len(documents), num_cores-1))
    num_doc = 0
    for doc in parser.pipe(documents, batch_size=batch_size, n_threads=num_cores - 1):
        print("\nCleaning Text for Document {}".format(num_doc+1))
        title = docs.df.loc[num_doc, 'title']
        if len(doc) > 1000:
            print("Chunking Document...")
            chunks, titles = split_text(doc, title, n_words=1000)
            titles_chunks.extend(titles)
            for chunk in chunks:
                doc_chunk = parser(chunk)
                cleaned_text, tokens = clean_document(doc_chunk)
                tokenized_docs.append(tokens)
            print("Tokenized docs: {}, Titles: {}".format(len(tokenized_docs), len(titles_chunks)))
        else:
            print("Document less than 1000 words")
            cleaned_text, tokens = clean_document(doc)
            tokenized_docs.append(tokens)
            titles_chunks.append(title)
            print("Tokenized docs: {}, Titles: {}".format(len(tokenized_docs), len(titles_chunks)))

        num_doc += 1

    return np.array(tokenized_docs), np.array(titles_chunks)


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

    STOPLIST = set(stopwords.words('english') + ["n't", "'s", "'m", "'", "'re", "'ve"] + \
                   ['philosophy', 'philosophers', 'philosopher', 'source', 'translator', \
                    'editor', 'tranlation', 'publication', 'version', 'material', 'mennen'] + \
                   [word.strip() for name in phils.df.name.values for word in name.split()] + \
                   [word.strip() for title in docs.df.title.values for word in title.split()] + \
                   list(ENGLISH_STOP_WORDS) + list([ch for ch in 'abcdefghijklmnopqrstuvwxyz']))

    tokenized_docs, all_titles = cleanse_corpus(full_texts, docs)
    print('Finished!  Beginning Next Process...')

    if len(tokenized_docs) == len(all_titles):
        print('\nPickling objects...')
        with open('data/model/tokenized_docs.pkl', 'wb') as f:
            pickle.dump(tokenized_docs, f)
        with open('data/model/chunk_titles.pkl', 'wb') as f:
            pickle.dump(all_titles, f)
    else:
        print(len(tokenized_docs), len(all_titles))
        print("Lengths don't match!")
