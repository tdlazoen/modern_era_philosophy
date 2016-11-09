import pandas as pd
import numpy as np
import scipy as scs
import pickle
import multiprocessing
import os
import pdb
from collections import defaultdict
from gensim.corpora import Dictionary
from gensim.matutils import corpus2dense, Dense2Corpus
from gensim.models.ldamodel import LdaModel
from gensim.models.ldamulticore import LdaMulticore
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity
from modern_dfs import ModernPhilosophers, ModernDocuments


def load_pickled(filename):
    with open(filename, 'rb') as f:
        data = pickle.load(f)

    return data


class LDA(object):

    '''
    A class for running lda on a gensim corpus object
    of documents
    '''

    def __init__(self, df, tokenized_docs, num_topics=200, workers=None, \
                 chunksize=None, random_state=42, multicore=True):
        '''
        PARAMETERS:
            df - dataframe containing information/text of documents
            tokenized_docs - An array of tokenized documents
            num_topics - number of topics to run lda with
            workers - number of processors to run in parallel
            chunksize - number of documents to process in a single chunk
            random_state - integer for numpy random seed
            multicore - whether or not to run lda in parallel
        '''
        self.df = df
        self.tokenized_docs = tokenized_docs
        self.num_topics = num_topics
        self.workers = workers
        self.chunksize = chunksize
        self.random_state = random_state
        self.multicore = multicore
        self.dictionary = Dictionary(self.tokenized_docs)
        self.filter_out_extremes()
        self.corpus = [self.dictionary.doc2bow(tokens) for tokens in tokenized_docs]

    def filter_out_extremes(self):
        self.dictionary.filter_extremes(no_below=10, no_above=0.9)

    def fit(self, normalize=True, run_lda=True):
        '''
        INPUT:
            tf_mat - term frequency matrix for corpus
            vocab - dictionary mapping words in corpus vocabulary
                    to unique ids
            run_lda - whether or not to run lda on tf_mat
        OUTPUT:
            None

        Run LDA using the term frequency matrix and record each
        document's topic distribution
        '''
        if self.workers is None:
            self.workers = multiprocessing.cpu_count() - 1

        if self.chunksize is None:
            self.chunksize = 0.3 * docs.df.shape[0]

        self.id2word = dict((v, k) for k, v in self.dictionary.token2id.items())

        if run_lda:
            params = {'num_topics': self.num_topics, 'id2word': self.id2word, \
                      'workers': self.workers, 'chunksize': self.chunksize, \
                      'random_state': self.random_state}

            if self.multicore:
                self.lda = LdaMulticore(corpus=self.normalized_corpus, **params, passes=20)
            else:
                self.lda = LdaModel(corpus=self.normalized_corpus, **params, passes=20)

    def doc_topic_dists(self):
        '''
        INPUT:
            None
        OUTPUT:
            None

        Find the topic distributions for all documents in self.df.  Sort
        ascending by id and place list of probabilities for topics 1-self.num_topics
        into new column called 'topic_dist'
        '''
        self.topic_weight_mat = np.zeros((self.df.shape[0], self.num_topics))

        doc_topics = []
        top_topics = []
        maxs = []
        for i, doc_bow in enumerate(self.corpus):
            topics = self.lda.get_document_topics(doc_bow, minimum_probability=0)
            sorted_topics = sorted(topics, key=lambda x: x[0])
            sorted_by_value = sorted(topics, key=lambda x: x[1], reverse=True)
            doc_topics.append(sorted_topics)
            top_topics.append([sorted_by_value[x][0] for x in range(5)])
            maxs.append(sorted_by_value[0][0])
            self.topic_weight_mat[i, :] = ([x[1] for x in sorted_topics])

        for i in range(5):
            self.df['top_topic_{}'.format(i+1)] = [x[i] for x in top_topics]
        self.most_important = np.unique(maxs)

    def top_words(self, topics=5, n_words=10):
        '''
        INPUT:
            topics - if list: a list of topics to get words for
                     if int: number of topics to get words for
                             (-1 gives back all topics)
            n_words - number of words to print out for each topic
        OUTPUT:
            None

        Prints out the (n_words) most probable words for topics or number of
        topics specified
        '''
        if isinstance(topics, int):
            if topics == -1:
                num_topics = self.num_topics
                topics = self.lda.show_topics(num_topics=num_topics, num_words=20, formatted=False)

        for topic in topics:
            print("\nShowing top {} most probable words for topic {}".format(n_words, topic[0]))
            for word, prob in sorted(topic[1], key=lambda x: x[1], reverse=True):
                print("Word: {} Probability: {}".format(word, prob))

    def print_most_important(self):
        for topicid in most_important:
            print("\nTopic id {}".format(topicid))
            lda.lda.print_topic(topicid)

    def top_topic_word_frequency(self, topic_id):
        '''
        INPUT:
            topic_id - topic unique identifier
        OUTPUT:
            (word, frequency) tuples for creating word cloud

        Get the term frequency for a certain topic (for word cloud)
        '''
        if topic_id in self.most_important:
            idxs = self.df[(self.df.top_topic_1 == topic_id) | (self.df.top_topic_2 == topic_id)].index.tolist()

            doc_term_freqs = corpus2dense(self.corpus, num_terms=len(self.dictionary.keys())).T
            topic_term_freqs = doc_term_freqs[idxs]

            freqs = np.sum(topic_term_freqs, axis=0)

            words = [dict(self.id2word)[i] for i in range(len(freqs))]

            return [(word, freq) for word, freq in zip(words, freqs)]
        else:
            return "Error!  The topic must be one of the most important"


if __name__ == '__main__':
    phils, docs = ModernPhilosophers(), ModernDocuments()

    print("Loading Model data...")
    parsed_docs = load_pickled('data/model/parsed_docs.pkl')
    tokenized_docs = load_pickled('data/model/tokenized_docs.pkl')

    print("Fitting LDA model...")
    lda = LDA(docs.df, tokenized_docs, num_topics=200, workers=56)
    lda.fit(run_lda=False)

    with open('data/model/lda_final.pkl', 'rb') as f:
        lda_best = pickle.load(f)

    lda.lda = lda_best.lda
    lda.doc_topic_dists()
