from flask import Flask, render_template, request, session, jsonify
from database import db
from models import Philosopher, Document, CurrentTopics, SimilarPhilosophers
import pickle
import numpy as np
import os
import sys
sys.path.append(os.path.abspath('..'))
from lda_topic_modeling import LDA


app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)

with open('../data/model/lda_25.pkl', 'rb') as f:
    model = pickle.load(f)


@app.route('/_phil_sum', methods=["GET"])
def phil_sum():
    name = request.args.get('name').lower()
    phil_info = Philosopher.query \
                           .filter(Philosopher.name == name) \
                           .first()

    similar_info = SimilarPhilosophers.query \
                                      .filter(SimilarPhilosophers.name == name) \
                                      .first()

    documents = Document.query \
                         .filter(Document.author == name) \
                         .all()

    dct = phil_info.serialize
    dct.update(similar_info.serialize)
    dct['documents'] = [doc.serialize for doc in documents]

    return jsonify(dct)


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
                               .filter(Document.year <= year, \
                                       Philosopher.year_died >= year, \
                                       Philosopher.year_born <= year) \
                               .distinct(Philosopher.name) \
                               .all()

    return jsonify(json_list=[phil.serialize for phil in current_phils])


@app.route('/_calculate_topics', methods=['GET'])
def calculate_topics():
    year = request.args.get('year', 1550, type=int)
    current_topics = CurrentTopics.query \
                                  .filter(CurrentTopics.year == year) \
                                  .first()

    return jsonify(json_list=current_topics.serialize)


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
    app.run(host='0.0.0.0', port=8000, threaded=True, debug=True)
