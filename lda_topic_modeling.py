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
from gensim.models.ldamulticore import LdaMulticore
from sklearn.metrics.pairwise import cosine_similarity
from modern_dfs import ModernPhilosophers, ModernDocuments


import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def load_pickled(filename):
    '''
    INPUT:
        filename - path to a pickle(.pkl) file
    OUTPUT:
        data - contents of pickle file
    '''
    with open(filename, 'rb') as f:
        data = pickle.load(f)

    return data


class LDA(object):

    '''
    A class for running lda on a gensim corpus object
    of documents
    '''

    def __init__(self, df, tokenized_docs, chunk_titles, num_topics=150, workers=None, \
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
        self.chunk_titles = chunk_titles
        self.num_topics = num_topics
        self.workers = workers
        self.chunksize = chunksize
        self.random_state = random_state
        self.multicore = multicore
        self.dictionary = Dictionary(self.tokenized_docs)
        self.filter_out_extremes()
        self.corpus = [self.dictionary.doc2bow(tokens) for tokens in tokenized_docs]

    def filter_out_extremes(self):
        '''
        INPUT:
            None
        OUTPUT:
            None

        Filters extreme occurences of words out from dictionary
        '''
        self.dictionary.filter_extremes(no_below=10, no_above=0.9)

    def fit(self, run_lda=True):
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
            self.chunksize = 2000

        self.id2word = dict((v, k) for k, v in self.dictionary.token2id.items())

        if run_lda:
            params = {'num_topics': self.num_topics, 'id2word': self.id2word, \
                      'workers': self.workers, 'chunksize': self.chunksize, \
                      'random_state': self.random_state}

            self.lda = LdaMulticore(corpus=self.corpus, passes=30, **params)

    def calculate_topic_weights(self):
        '''
        INPUT:
            None
        OUTPUT:
            None

        Find the topic distributions for all documents in self.df.  Sort
        ascending by id and place list of probabilities for topics 1-self.num_topics
        into new column called 'topic_dist'
        '''
        self.topic_weight_mat = np.zeros((len(self.corpus), self.num_topics))

        for i, doc_bow in enumerate(self.corpus):
            topics = self.lda.get_document_topics(doc_bow, minimum_probability=0)
            sorted_topics = sorted(topics, key=lambda x: x[0])
            self.topic_weight_mat[i, :] = ([x[1] for x in sorted_topics])

    def group_doc_chunks(self):
        '''
        INPUT:
            None
        OUTPUT:
            None

        Groups document chunk probabilities together
        '''
        all_docs = []
        for i, title in enumerate(self.df.title.values):
            doc_chunks = self.topic_weight_mat[self.chunk_titles == title]
            doc_topic_probs = list(np.sum(doc_chunks, axis=0) / np.sum(doc_chunks))
            doc_ids_to_probs = [(topic, prob) for topic, prob in enumerate(doc_topic_probs)]
            all_docs.append(doc_ids_to_probs)

        self.topic_dists = [(title, topic_prob_lst) for title, topic_prob_lst in \
                            zip(lda.df.title.values, all_docs)]

    def get_philosopher_distributions(self):
        self.philosopher_topic_dists = []

        for name in self.df.author.unique():
            phil_df = self.df[self.df.author == name]
            titles = phil_df.title.values
            mask = np.in1d(self.chunk_titles, titles)
            phil_weights = self.topic_weight_mat[mask]
            phil_dist = np.sum(phil_weights, axis=0) / np.sum(phil_weights)
            self.philosopher_topic_dists.append((name, phil_dist))

    def get_similar_philosophers(self):
        model.philosopher_cosine_sims = []
        for name, vector in model.philosopher_topic_dists:
            cos_sims = []
            for name2, vector2 in model.philosopher_topic_dists:
                if name2 == name:
                    continue
                else:
                    cos_sim = cosine(vector, vector2)
                    cos_sims.append((name2, cos_sim))
            ordered_cos = sorted(cos_sims, key=lambda x: x[1], reverse=True)
            sim_dict = {'name': name, \
                        'first': ordered_cos[0][0], \
                        'second': ordered_cos[1][0], \
                        'third': ordered_cos[2][0], \
                        'fourth': ordered_cos[3][0], \
                        'fifth': ordered_cos[4][0] }
            model.philosopher_cosine_sims.append(sim_dict)

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

    def topic_word_frequency(self, topic_id):
        '''
        INPUT:
            topic_id - topic unique identifier
        OUTPUT:
            (word, frequency) tuples for creating word cloud

        Get the term frequency for a certain topic (for word cloud)
        '''
        idxs = []
        for i in range(self.topic_weight_mat.shape[0]):
            topic_weights = self.topic_weight_mat[i, :]
            top_topic = np.argsort(topic_weights)[-1]
            if topic_id == top_topic:
                idxs.append(i)

        mask = np.array(idxs)

        doc_term_freqs = corpus2dense(self.corpus, num_terms=len(self.dictionary.keys())).T
        topic_term_freqs = doc_term_freqs[mask]

        freqs = np.sum(topic_term_freqs, axis=0)

        words = [dict(self.id2word)[i] for i in range(len(freqs))]

        return [(word, freq) for word, freq in zip(words, freqs)]


# if __name__ == '__main__':
#     phils, docs = ModernPhilosophers(), ModernDocuments()
#     np.random.seed(42)
#
#     print("Loading Model data...")
#     all_titles = load_pickled('data/model/chunk_titles_final.pkl')
#     tokenized_docs = load_pickled('data/model/tokenized_docs_final.pkl')
#
#     print("Fitting LDA model...")
#     lda = LDA(docs.df, tokenized_docs, all_titles, num_topics=25, workers=56)
#     lda.fit(run_lda=True)
#
#     # with open('data/model/lda_50.pkl', 'rb') as f:
#     #     lda_best = pickle.load(f)
#
#     print("Getting topic weights...")
#     lda.calculate_topic_weights()
#     print("Grouping Chunks...")
#     lda.group_doc_chunks()
#
#     with open('data/model/lda_25.pkl', 'wb') as f:
#         pickle.dump(lda, f)
