import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dataframes import Philosophers, Documents

if __name__ == '__main__':
	phils = Philosophers(filepath='../data/philosophers.csv')
	docs = Documents(filepath='../data/documents.csv')
