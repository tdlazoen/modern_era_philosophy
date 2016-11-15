from app import db
from models import Philosopher, Document
import os
import sys
sys.path.append(os.path.abspath('..'))
from modern_dfs import ModernPhilosophers, ModernDocuments

def add_initial():
    '''
    INPUT:
        None
    OUTPUT:
        None

    Fills philosopher and document databases with
    dataframe data
    '''
    phils, docs = ModernPhilosophers(filepath='../data/modern_philosophers.csv'), \
                  ModernDocuments(filepath='../data/modern_documents.csv')

    for i in range(phils.df.shape[0]):
        phil_params = {'name': phils.df.loc[i, 'name'], \
                         'nationality': phils.df.loc[i, 'nationality'], \
                         'birthplace': phils.df.loc[i, 'birthplace'], \
                         'year_born': int(phils.df.loc[i, 'year_born']), \
                         'year_died': int(phils.df.loc[i, 'year_died']), \
                         'time_period': phils.df.loc[i, 'time_period'], \
                         'image_path': phils.df.loc[i, 'image_path'], \
                         'summary': phils.df.loc[i, 'summary'], \
                         'latitude': phils.df.loc[i, 'latitude'], \
                         'longitude': phils.df.loc[i, 'longitude']}

        phil = Philosopher(**phil_params)
        db.session.add(phil)

        name_idxs = docs.df[docs.df.author == phils.df.loc[i, 'name']].index.tolist()
        for j in name_idxs:
            doc_params = {'author': docs.df.loc[j, 'author'], \
                          'title': docs.df.loc[j, 'title'], \
                          'year': int(docs.df.loc[j, 'year']), \
                          'century': int(docs.df.loc[j, 'century']), \
                          'text': docs.df.loc[j, 'text'], \
                          'words': int(docs.df.loc[j, 'words']), \
                          'url': docs.df.loc[j, 'url'], \
                          'filepath': docs.df.loc[j, 'filepath']}
            doc = Document(**doc_params)
            db.session.add(doc)

    db.session.commit()

def remove_initial():
    for philosopher in Philosopher.query.all():
        db.session.delete(philosopher)

    for document in Document.query.all():
        db.session.delete(document)

    db.session.commit()
