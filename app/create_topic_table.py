from app import db
from models import Philosopher, Document, CurrentTopics, SimilarPhilosophers
import pickle
import numpy as np
import os
import sys
sys.path.append(os.path.abspath('..'))
from modern_dfs import ModernPhilosophers
from lda_topic_modeling import LDA

def add_topic_table():
    with open('../data/model/lda_25.pkl', 'rb') as f:
        model = pickle.load(f)

    for year in range(1550, 2017):
        current_docs = Document.query \
                                 .join(Philosopher, \
                                       Document.author == Philosopher.name) \
                                 .filter(Document.year <= year, \
                                         Philosopher.year_died >= year, \
                                         Philosopher.year_born <= year) \
                                 .all()
        if len(current_docs) > 0:
            current_titles = np.array([doc.title for doc in current_docs])
            mask = np.in1d(model.chunk_titles, current_titles)
            current_topic_weights = model.topic_weight_mat[mask]
            topic_probs = np.sum(current_topic_weights, axis=0) / np.sum(current_topic_weights)

            top_5_topics = np.argsort(topic_probs)[::-1][:5]
            topic_probs = topic_probs[top_5_topics]

            topic_names = []
            for topicid in top_5_topics:
                topic_names.append(model.topic_dict[topicid])

            current_params = {'year': year, \
                              'first_id': int(top_5_topics[0]), \
                              'first_title': topic_names[0], \
                              'first_prob': topic_probs[0], \
                              'second_id': int(top_5_topics[1]), \
                              'second_title': topic_names[1], \
                              'second_prob': topic_probs[1], \
                              'third_id': int(top_5_topics[2]), \
                              'third_title': topic_names[2], \
                              'third_prob': topic_probs[2], \
                              'fourth_id': int(top_5_topics[3]), \
                              'fourth_title': topic_names[3], \
                              'fourth_prob': topic_probs[3], \
                              'fifth_id': int(top_5_topics[4]), \
                              'fifth_title': topic_names[4], \
                              'fifth_prob': topic_probs[4]}
        else:
            current_params = {'year': year, \
                              'first_id': 0, \
                              'first_title': '', \
                              'first_prob': 0, \
                              'second_id': 0, \
                              'second_title': '', \
                              'second_prob': 0, \
                              'third_id': 0, \
                              'third_title': '', \
                              'third_prob': 0, \
                              'fourth_id': 0, \
                              'fourth_title': '', \
                              'fourth_prob': 0, \
                              'fifth_id': 0, \
                              'fifth_title': '', \
                              'fifth_prob': 0}
        year_topics = CurrentTopics(**current_params)
        db.session.add(year_topics)

    db.session.commit()


def similar_philosophers_table():
    with open('../data/model/lda_25.pkl', 'rb') as f:
        model = pickle.load(f)

    for dct in model.philosopher_cosine_sims:
        params = {'name': dct['name'], \
                  'first_name': dct['first'], \
                  'second_name': dct['second'], \
                  'third_name': dct['third'], \
                  'fourth_name': dct['fourth'], \
                  'fifth_name': dct['fifth']}

        similar_phils = SimilarPhilosophers(**params)
        db.session.add(similar_phils)

    db.session.commit()
