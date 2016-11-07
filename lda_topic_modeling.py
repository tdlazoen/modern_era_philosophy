import pandas as pd
import numpy as np
import pickle
import multiprocessing
import os
from gensim.matutils import Sparse2Corpus
from gensim.corpora import Dictionary
from gensim.models.ldamulticore import LdaMulticore
from gensim.models.ldamodel import LdaModel
from modern_dfs import ModernPhilosophers, ModernDocuments


def load_pickled(filename):
    with open(filename, 'rb') as f:
        data = pickle.load(f)

    return data


def create_gensim_objects(tf_mat, vect):
    corpus = Sparse2Corpus(tf_mat)

    id_word_dict = dict((v, k) for k, v in vect.vocabulary_.items())
    vocab_dct = Dictionary.from_corpus(corpus, id2word=id_word_dict)

    return corpus, vocab_dct


class LDA(object):

    '''
    A class for running lda on a gensim corpus object
    of documents
    '''

    def __init__(self, corpus, num_topics=10, id2word=None, \
                 workers=None, chunksize=None, random_state=42, \
                 multicore=True):
        '''
        PARAMETERS:
            corpus - a gensim corpus object of word vectors
            num_topics - number of topics to run lda with
            id2word - dictionary mapping "ids" to words
            workers - number of processors to run in parallel
            chunksize - number of documents to process in a single chunk
            random_state - integer for numpy random seed
            multicore - whether or not to run lda in parallel
        '''
        self.corpus = corpus
        self.sparse = self.corpus.sparse
        self.tf = self.sparse.toarray()
        self.num_topics = num_topics
        self.id2word = id2word
        self.set_workers(workers)
        self.set_chunksize(chunksize)
        self.random_state = random_state
        self.multicore = multicore


    def set_workers(self, workers):
        if workers is None:
            workers = multiprocessing.cpu_count() - 1
        self.workers = workers

    def set_chunksize(self, chunksize):
        if chunksize is None:
            chunksize = 0.1 * self.sparse.shape[0]
        self.chunksize = chunksize

    def fit(self):
        params = {'corpus': self.corpus, 'num_topics': self.num_topics, \
                  'id2word': self.id2word, 'workers': self.workers, \
                  'chunksize': self.chunksize, 'random_state': self.random_state}
        if self.multicore:
            self.lda = LdaMulticore(**params)
        else:
            self.lda = LdaModel(**params)


if __name__ == '__main__':
    phils, docs = ModernPhilosophers(), ModernDocuments()

    print("Loading Model data...")
    vectorizer = load_pickled('data/model/vectorizer.pkl')
    tf_matrix = load_pickled('data/model/tf_matrix.pkl')
    tokenized_words = load_pickled('data/model/parsed_docs.pkl')

    print("\nGenerating Corpus...")
    corpus, id2word_dict = create_gensim_objects(tf_matrix, vectorizer)

    print("\nInstantiating LDA object...")
    lda = LDA(corpus, num_topics=20, id2word=id2word_dict)
    print("Fitting LDA object to corpus...")
    lda.fit()
    print("Finished!")
