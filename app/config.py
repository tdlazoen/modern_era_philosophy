import os
basedir = os.path.expanduser('~') + '/philosophy_capstone/app/'

WTF_CSRF_ENABLED = True
SECRET_KEY = 'Myfavouritecatintheworldissnicker5'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True

WHOOSH_BASE = os.path.join(basedir, 'search.db')
