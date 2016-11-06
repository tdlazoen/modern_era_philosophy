import pandas as pd
import numpy as np
import pickle
from gensim.matutils import Sparse2Corpus
from gensim.corpora import Dictionary
from gensim.models import ldamulticore
from modern_dfs import ModernPhilosophers, ModernDocuments


def load_pickled(filename):
    with open(filename, 'rb') as f:
        data = pickle.load(f)

    return vectorizer, tf_matrix, tokenized_words


def create_gensim_objects(tf_mat, vect):
    corpus = Sparse2Corpus(tf_mat)

    id_word_dict = dict((v, k) for k, v in vect.vocabulary_.items())
    vocab_dct = Dictionary.from_corpus(corpus, id2word=id_word_dict)

    return corpus, vocab_dct


def run_lda(tf_mat):
    


if __name__ == '__main__':
    phils, docs = ModernPhilosophers(), ModernDocuments()

    vectorizer = load_pickled('data/model/vectorizer.pkl')
    tf_matrix = load_pickled('data/model/tf_matrix.pkl')
    tokenized_words = load_pickled('data/model/tokenized_words.pkl')
