import os
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

WTF_CSRF_ENABLED = True
SECRET_KEY = 'Myfavouritecatintheworldissnicker5'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(PROJECT_ROOT, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True
