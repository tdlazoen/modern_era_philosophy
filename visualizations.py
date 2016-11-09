import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
from lda_topic_modeling import LDA, get_important_topics
from modern_dfs import ModernDocuments, ModernPhilosophers

def topics_vs_threshold(figsize=(10, 8), filepath=None):
    '''
    INPUT:
        figsize - figure size of plot
        filepath - path to save image to
    OUTPUT:
        None

    Plots different word probability thresholds vs. number of topics
    above threshold from 200 topic LDA Model
    '''
    with open('data/model/lda_class.pkl', 'rb') as f:
        lda_class = pickle.load(f)

    thresholds = [0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.97, 0.98]

    num_topics = [get_important_topics(lda_class.lda, x) for x in thresholds]

    with plt.style.context(('ggplot')):
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(1, 1, 1)
        x = thresholds
        y = num_topics
        ax.plot(x, y, lw=2, c='b', marker='o', markersize=5, \
                alpha=0.6)
        ax.set_title("Number of topics vs. thresholds", fontsize=20)
        ax.set_xlabel("Threshold (sum of topic word probabilities)", fontsize=14)
        ax.set_ylabel("Number of topics", fontsize=14)
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


if __name__ == '__main__':
    # topics_vs_threshold(filepath='visualizations/topics_thresholds.png')
    docs_by_century(filepath='visualizations/docs_century.png')
    docs_by_philosopher(filepath='visualizations/docs_philosopher.png')
