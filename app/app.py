from flask import Flask, render_template, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from database import db_session, init_db
from models import Philosopher, Document
import pickle
import pandas as pd
import numpy as np


app = Flask(__name__)
app.config.from_object('config')


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove


# Main page
@app.route('/', method=["GET"])
def home():
    '''
    INPUT:
        None
    OUTPUT:
        Main page template
    '''
    return render_template("index.html")

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8000, threaded=True, debug=True)
