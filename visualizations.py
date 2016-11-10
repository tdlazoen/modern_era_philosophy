import pandas as pd
import numpy as np
import pickle
import pdb
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from nltk.corpus import stopwords
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from collections import Counter, defaultdict
from lda_topic_modeling import LDA
from modern_dfs import ModernDocuments, ModernPhilosophers

def lda_mean_word_probs(figsize=(10, 8), filepath=None):
    with open('data/model/lda.pkl', 'rb') as f:
        lda = pickle.load(f)

    max_word_probs = []
    topics = []
    all_topics = lda.lda.show_topics(num_topics=lda.num_topics, \
                 num_words=10000, formatted=False)
    for topic, word_probs in all_topics:
        max_prob = np.max([x[1] for x in word_probs])
        max_word_probs.append(max_prob)

    with plt.style.context(("ggplot")):
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(1, 1, 1)

        ax.hist(max_word_probs, histtype='stepfilled', color='g', \
                bins=100, alpha=0.7)

        ax.set_title("Distribution of max word probabilities for 200-topic LDA model")
        ax.set_xlabel("Max word probability", fontsize=14)
        ax.set_ylabel("Number of topics with max probability", fontsize=14)
        ax.set_xlim(0, 0.1)

        plt.show()

        if filepath:
            plt.savefig(filepath, bbox_inches='tight')

def docs_by_century(figsize=(10, 8), filepath=None):
    '''
    INPUT:
        figsize - figure size of plot
        filepath - path to save image to
    OUTPUT:
        None

    Plots number of documents written per century
    '''
    docs = ModernDocuments()

    centuries = np.unique(docs.df.century.values)

    with plt.style.context(('ggplot')):
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(1, 1, 1)

        left = [cent + 50 for cent in centuries]
        height = [docs.df[docs.df.century == cent].shape[0] for cent in centuries]
        tick_labels = centuries

        ax.bar(left, height, color='g', tick_label=tick_labels, width=80, \
               align='center', linewidth=0, alpha=0.6)
        ax.set_title("Number of documents by century", fontsize=20)
        ax.set_xlabel("Century", fontsize=14)
        ax.set_ylabel("Number of documents", fontsize=14)

        plt.show()

        if filepath:
            plt.savefig(filepath, bbox_inches='tight')

def docs_by_philosopher(figsize=(10, 8), filepath=None):
    '''
    INPUT:
        figsize - figure size of plot
        filepath - path to save image to
    OUTPUT:
        None

    Plots distribution of philosophers based on number
    of documents
    '''
    phils = ModernPhilosophers()
    docs = ModernDocuments()
    counts = []
    for i in range(phils.df.shape[0]):
        name = phils.df.loc[i, 'name']
        num_docs = docs.df[docs.df.author == name].shape[0]
        counts.append(num_docs)

    with plt.style.context(('ggplot')):
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(1, 1, 1)

        ax.hist(counts, bins=len(np.unique(counts)), color='m', \
                histtype='stepfilled', alpha=0.6)

        ax.set_title("Distribution of number of documents written by philosophers")
        ax.set_xlabel("Number of documents")
        ax.set_ylabel("Number of philosophers")

        plt.show()

        if filepath:
            plt.savefig(filepath, bbox_inches='tight')


def word_distribution_plots(figsize=(16, 10), filepath=None):
    with open('data/model/tokenized_docs.pkl', 'rb') as f:
        tokenized_docs = pickle.load(f)

    all_text = ''
    for tokens in tokenized_docs:
        all_text += ' '.join(token for token in tokens)

    word_counts = Counter(all_text.split())

    doc_freqs = defaultdict(int)

    for word in word_counts.keys():
        for tokens in tokenized_docs:
            if word in tokens:
                doc_freqs[word] += 1

    with plt.style.context("ggplot"):
        fig = plt.figure(figsize=figsize)
        # Plot word count distribution
        ax1 = fig.add_subplot(2, 1, 1)
        x1 = word_counts.values()
        ax1.hist(x1, bins=100, normed=True, histtype='stepfilled', \
                 color='b')
        ax1.set_title("Normalized distribution of term frequencies", fontsize=20)
        ax1.set_xlabel("Word", fontsize=14)
        ax1.set_ylabel("Term frequency", fontsize=14)

        ax2 = fig.add_suplot(2, 1, 2)
        x2 = doc_freqs.values()

        ax2.hist(x2, bins=100, normed=True, hisstype='stepfilled', \
                 color='c')

        ax2.set_title("Normalized distribution of document frequencies", fontsize=20)
        ax2.set_xlabel("Word", fontsize=14)
        ax2.set_ylabel("Document frequency", fontsize=14)

        if filepath:
            plt.savefig(filepath, bbox_inches='tight')

def document_length_distribution(figsize=(16, 10), filepath=None):
    docs = ModernDocuments()
    words = docs.df.words.values
    maxx = np.max(words)
    minn = np.min(words)
    mean = np.mean(words)

    with plt.style.context(('ggplot')):
        fig = plt.figure(figsize=figsize)
        ax1 = fig.add_subplot(1, 2, 1)

        ax1.hist(words, bins=215, histtype="stepfilled", color='c')
        ax1.set_title("Distribution of document lengths", fontsize=20)
        ax1.set_xlabel("Document length", fontsize=14)
        ax1.set_ylabel("Number of documents with each length", fontsize=14)
        xlim1 = ax1.get_xlim()
        ax1.set_xticks(xlim1)

        ax2 = fig.add_subplot(1, 2, 2)

        words_under_threshold = [num_words for num_words in words if num_words < 100000]

        ax2.hist(words, bins=len(words_under_threshold), histtype="stepfilled", color='c')
        ax2.set_title("Distribution of document lengths", fontsize=20)
        ax2.set_xlabel("Document length", fontsize=14)
        ax2.set_ylabel("Number of documents with each length", fontsize=14)
        ax2.set_xlim(0, 100000)
        ax2.set_xticks([0, 100000])

        plt.tight_layout()
        plt.show()

        plt.savefig(filepath, bbox_inches='tight')


def word_cloud(model_file, base_filepath):
    phils = ModernPhilosophers()

    STOPLIST = set(stopwords.words('english') + ["n't", "'s", "'m", "'", "'re", "'ve"] + \
                   ['philosophy', 'philosophers', 'philosopher', 'source', 'translator', \
                    'editor', 'tranlation', 'publication', 'version', 'material', 'mennen'] + \
                   [word.strip() for name in phils.df.name.values for word in name.split()] + \
                   [word.strip() for title in docs.df.title.values for word in title.split()] + \
                   list(ENGLISH_STOP_WORDS) + list([ch for ch in 'abcdefghijklmnopqrstuvwxyz']))

    with open(model_file, 'rb') as f:
        lda = pickle.load(f)

    for topic in lda.most_important:
        wordcloud = WordCloud(background_color="white")
        term_freqs = lda.top_topic_word_frequency(topic)
        wordcloud.fit_words(term_freqs)

        filepath_topic = filepath + '_topic{}.png'.format(topic)

        wordcloud.to_file(filepath_topic)

if __name__ == '__main__':
    # topics_vs_threshold(filepath='visualizations/topics_thresholds.png')
    # docs_by_century(filepath='visualizations/docs_century.png')
    # docs_by_philosopher(filepath='visualizations/docs_philosopher.png')
    word_distribution_plots(filepath='visualizations/word_distributions.png')
    # lda_mean_word_probs(filepath='visualizations/lda-200-word-probs.png')
    # document_length_distribution(filepath='visualizations/document_lengths.png')
    # word_cloud(model_file='data/model/lda_200.pkl', base_filepath='visualizations/lda200')
