from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float


db = SQLAlchemy()


class Philosopher(db.Model):
    __tablename__ = 'philosophers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    nationality = db.Column(db.String)
    birthplace = db.Column(db.String)
    year_born = db.Column(db.Integer)
    year_died = db.Column(db.Integer)
    time_period = db.Column(db.String)
    image_path = db.Column(db.String)
    summary = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    def __init__(self, name, nationality, birthplace, year_born, \
                 year_died, time_period, image_path, summary, latitude, \
                 longitude):
        self.name = name
        self.nationality = nationality
        self.birthplace = birthplace
        self.year_born = year_born
        self.year_died = year_died
        self.time_period = time_period
        self.image_path = image_path
        self.summary = summary
        self.latitude = latitude
        self.longitude = longitude

    @property
    def serialize(self):
        return {'id': self.id,
                'name': self.name,
                'nationality': self.nationality,
                'birthplace': self.birthplace,
                'country': self.country,
                'year_born': self.year_born,
                'year_died': self.year_died,
                'time_period': self.time_period,
                'image_path': self.image_path,
                'summary': self.summary,
                'latitude': self.latitude,
                'longitude': self.longitude}


class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('philosophers.id'))
    author = db.Column(db.String)
    year = db.Column(db.Integer)
    century = db.Column(db.Integer)
    text = db.Column(db.String)
    words = db.Column(db.Integer)
    url = db.Column(db.String)
    filepath = db.Column(db.String)
    # cluster = db.Column(db.Integer)

    def __init__(self, author, year, century, text, words, url, filepath):
        self.author = author
        self.year = year
        self.century = century
        self.text = text
        self.words = words
        self.url = url
        self.filepath = filepath

    @property
    def serialize(self):
        return {'id': self.id,
                'author_id': self.author_id,
                'author': self.author,
                'year': self.year,
                'century': self.century,
                'text': self.text,
                'words': self.words,
                'url': self.url,
                'filepath': self.filepath}
