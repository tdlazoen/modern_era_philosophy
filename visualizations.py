import pandas as pd
import numpy as np
import pickle
import pdb
import os
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from nltk.corpus import stopwords
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from collections import Counter, defaultdict
from lda_topic_modeling import LDA
from modern_dfs import ModernDocuments, ModernPhilosophers

def lda_word_dists(lda_model, figsize=(16, 10), filepath=None):
    '''
    INPUT:
        lda_model - LDA class instance
        figsize - size of figure
        filepath - path to save figure to
    OUTPUT:
        None

    Plots the maximum and mean word probabilites associated
    with each topic from lda_model
    '''
    max_word_probs = list(np.max(lda_model.topic_weight_mat, axis=0))
    mean_word_probs = list(np.mean(lda_model.topic_weight_mat, axis=0))

    num_topics = lda_model.num_topics

    with plt.style.context(("ggplot")):
        fig = plt.figure(figsize=figsize)
        ax1 = fig.add_subplot(1, 2, 1)

        ax1.hist(max_word_probs, histtype='stepfilled', color='b', \
                bins=num_topics, alpha=0.6)

        avg_max = np.mean(max_word_probs)
        ax1.axvline(avg_max, lw=3, c='r', linestyle='dashed', alpha=0.8, \
                    label='Mean: {}'.format(np.round(avg_max, 3)))

        ax1.set_title("Distribution of max word probabilities for {}-topic LDA model".format(num_topics), fontsize=40)
        ax1.set_xlabel("Max word probability", fontsize=30)
        ax1.set_ylabel("Number of topics", fontsize=30)

        ax1.tick_params(axis='x', labelsize=20)
        ax1.tick_params(axis='y', labelsize=20)

        ax1.legend(loc='best')

        ax2 = fig.add_subplot(1, 2, 2)

        ax2.hist(mean_word_probs, histtype='stepfilled', color='b', \
                 bins=num_topics, alpha=0.6)

        avg_mean = np.mean(mean_word_probs)
        ax2.axvline(avg_mean, lw=3, c='r', linestyle='dashed', alpha=0.8, \
                    label='Mean: {}'.format(np.round(avg_mean, 3)))

        ax2.set_title("Distribution of mean word probabilities for {}-topic LDA model".format(num_topics), fontsize=40)
        ax2.set_xlabel("Mean word probability", fontsize=30)
        ax2.set_ylabel("Number of topics", fontsize=30)
        ax2.legend(loc='best')

        ax2.tick_params(axis='x', labelsize=20)
        ax2.tick_params(axis='y', labelsize=20)

        plt.tight_layout()
        plt.show()

        if filepath:
            plt.savefig(filepath, bbox_inches='tight')

def topic_distribution(lda_model, figsize=(10, 8), filepath=None):
    '''
    INPUT:
        lda_model - LDA class instance
        figisize - size of figure
        filepath - path to save figure to
    OUTPUT:
        None

    Plots the distribution of topics learned from LDA among
    the entire corpus of documents
    '''
    max_topics = []

    for i in range(len(lda_model.corpus)):
        max_idx = np.argsort(lda_model.topic_weight_mat[i, :])[-1]
        max_topics.append(max_idx)

    num_topics = lda_model.num_topics

    with plt.style.context(('ggplot')):
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(1, 1, 1)

        ax.hist(max_topics, histtype='stepfilled', color='b', bins=num_topics, \
                alpha=0.6)

        ax.set_title("Top topic distribution for {}-topic LDA model".format(num_topics), fontsize=40)
        ax.set_xlabel("Top topic", fontsize=30)
        ax.set_ylabel("Number of documents", fontsize=30)
        ax.set_xlim(0, num_topics)

        ax.tick_params(axis='x', labelsize=20)
        ax.tick_params(axis='y', labelsize=20)

        plt.tight_layout()
        plt.show()

        if filepath:
            plt.savefig(filepath, bbox_inches='tight')

def docs_by_century(docs, figsize=(10, 8), filepath=None):
    '''
    INPUT:
        docs - documents dataframe
        figsize - figure size of plot
        filepath - path to save image to
    OUTPUT:
        None

    Plots number of documents written per century
    '''

    centuries = np.unique(docs.df.century.values)

    with plt.style.context(('ggplot')):
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(1, 1, 1)

        left = [cent + 50 for cent in centuries]
        height = [docs.df[docs.df.century == cent].shape[0] for cent in centuries]
        tick_labels = centuries

        ax.bar(left, height, color='b', tick_label=tick_labels, width=80, \
               align='center', linewidth=0, alpha=0.6)
        ax.set_title("Documents by century", fontsize=40)
        ax.set_xlabel("Century", fontsize=30)
        ax.set_ylabel("Number of documents", fontsize=30)

        ax.tick_params(axis='x', labelsize=20)
        ax.tick_params(axis='y', labelsize=20)

        plt.tight_layout()
        plt.show()

        if filepath:
            plt.savefig(filepath, bbox_inches='tight')

def docs_by_philosopher(phils, docs, figsize=(10, 8), filepath=None):
    '''
    INPUT:
        phils - philosopher dataframe
        docs - documents dataframe
        figsize - figure size of plot
        filepath - path to save image to
    OUTPUT:
        None

    Plots distribution of philosophers based on number
    of documents
    '''
    counts = []

    for i in range(phils.df.shape[0]):
        name = phils.df.loc[i, 'name']
        num_docs = docs.df[docs.df.author == name].shape[0]
        counts.append(num_docs)

    with plt.style.context(('ggplot')):
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(1, 1, 1)

        ax.hist(counts, bins=len(np.unique(counts)), color='b', \
                histtype='stepfilled', alpha=0.6)

        ax.set_title("Distribution of documents", fontsize=40)
        ax.set_xlabel("Number of documents", fontsize=30)
        ax.set_ylabel("Number of philosophers", fontsize=30)

        ax.tick_params(axis='x', labelsize=20)
        ax.tick_params(axis='y', labelsize=20)

        plt.tight_layout()
        plt.show()

        if filepath:
            plt.savefig(filepath, bbox_inches='tight')


def document_length_distribution(docs, figsize=(12, 10), filepath=None):
    '''
    INPUT:
        docs - documents dataframe
        figsize - size of figure
        filepath - path to save figure to
    OUTPUT:
        None

    Plots a histogram of document lengths based off of
    words column in documents dataframe
    '''
    words = docs.df.words.values
    maxx = np.max(words)
    minn = np.min(words)
    mean = np.mean(words)

    with plt.style.context(('ggplot')):
        fig = plt.figure(figsize=figsize)
        ax1 = fig.add_subplot(1, 1, 1)

        ax1.hist(words, bins=215, histtype="stepfilled", color='b', alpha=0.6)
        ax1.set_title("Distribution of document lengths", fontsize=40)
        ax1.set_xlabel("Document length", fontsize=30)
        ax1.set_ylabel("Number of documents", fontsize=30)
        ax1.set_xlim(0, 100000)
        ax1.xaxis.set_ticks([0, 100000])

        ax1.tick_params(axis='x', labelsize=20)
        ax1.tick_params(axis='y', labelsize=20)

        plt.tight_layout()
        plt.show()

        if filepath:
            plt.savefig(filepath, bbox_inches='tight')


def word_cloud(lda_model, topic, filepath):
    '''
    INPUT:
        lda_model - LDA class instance
        topic - topic id to make word cloud for
        filepath - path to save word cloud to
    OUTPUT:
        None

    Saves a word cloud for topic id to specified filename
    '''
    if not os.path.exists(filepath):
        wordcloud = WordCloud(background_color="white", stopwords={'law', 'pair'})
        term_freqs = lda_model.topic_word_frequency(topic)
        wordcloud.fit_words(term_freqs)

        wordcloud.to_file(filepath)
    else:
        print("Already exists!")

if __name__ == '__main__':
    with open('data/model/lda_25.pkl', 'rb') as f:
        lda = pickle.load(f)

    phils, docs = ModernPhilosophers(), ModernDocuments()

    docs_by_century(docs, filepath='visualizations/data_vis/docs_century.png')
    docs_by_philosopher(phils, docs, filepath='visualizations/data_vis/docs_philosopher.png')
    word_distribution_plots(docs, filepath='visualizations/data_vis/word_distributions.png')
    lda_word_dists(lda, filepath='visualizations/data_vis/lda-25-word-dists.png')
    topic_distribution(lda, filepath='visualizations/data_vis/lda-25-topic-dist.png')
    document_length_distribution(docs, filepath='visualizations/data_vis/document_lengths.png')
    for topic_id in range(lda.num_topics):
        print("Getting word cloud for topic {}".format(topic_id))
        filepath = 'visualizations/word_clouds/topics_25/topic{}.png'.format(topic_id)
        word_cloud(lda, topic_id, filepath)
