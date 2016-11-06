from flask import Flask, render_template, request, session, jsonify
import pickle
import pandas as pd
import numpy as np


app = Flask(__name__)


# Main page
@app.route('/')
def home():
    '''
    INPUT:
        None
    OUTPUT:
        Home page template
    '''
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)
