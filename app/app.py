from flask import Flask, render_template, request, session, jsonify
from database import db
from models import Philosopher, Document
import pickle
import numpy as np
import os
import sys
sys.path.append(os.path.abspath('..'))
from lda_topic_modeling import LDA


app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)


@app.route('/_jump_to_phil', methods=["GET"])
def jump_to_philosopher():
    name = request.args.get('name').lower()
    first_document = Document.query \
                            .join(Philosopher, \
                                  Document.author == Philosopher.name) \
                            .filter(Document.author == name) \
                            .order_by(Document.year) \
                            .first()

    return jsonify(first_document.serialize)


@app.route('/_current_phils', methods=["GET"])
def current_philosophers():
    year = request.args.get('year', 1550, type=int)
    current_phils = Philosopher.query \
                               .join(Document, \
                                     Philosopher.name == Document.author) \
                               .filter(Document.year >= year, \
                                       Philosopher.year_died >= year, \
                                       Philosopher.year_born <= year) \
                               .distinct(Philosopher.name) \
                               .all()

    return jsonify(json_list=[phil.serialize for phil in current_phils])


@app.route('/_calculate_topics', methods=['GET'])
def calculate_topics():
    year = request.args.get('year', 1550, type=int)
    current_docs = Document.query \
                             .join(Philosopher, \
                                   Document.author == Philosopher.name) \
                             .filter(Document.year >= year, \
                                     Philosopher.year_died >= year, \
                                     Philosopher.year_born <= year) \
                             .all()

    current_titles = np.array([doc.title for doc in current_docs])
    mask = np.in1d(model.chunk_titles, current_titles)
    current_topic_weights = model.topic_weight_mat[mask]
    topic_probs = np.sum(current_topic_weights, axis=0) / np.sum(current_topic_weights)

    top_10_topics = np.argsort(topic_probs)[::-1][:10]

    current_topics = [dict([('title', model.topic_dict[topic_num]), \
                           ('probability', topic_probs[topic_num])]) for topic_num in top_10_topics]

    ordered_topics = sorted(current_topics, key=lambda x: x['probability'], reverse=True)

    return jsonify(json_list=current_topics)


# Main page
@app.route('/', methods=["GET"])
def home():
    '''
    INPUT:
        None
    OUTPUT:
        Main page template
    '''
    return render_template("index_with_visual.html")


if __name__ == '__main__':
    with open('../data/model/lda_25.pkl', 'rb') as f:
        model = pickle.load(f)

    app.run(host='0.0.0.0', port=8080, threaded=True, debug=True)
