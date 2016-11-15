from database import db
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship


class Philosopher(db.Model):
    __searchable__ = 'name'
    __tablename__ = 'philosophers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    nationality = db.Column(db.String(50))
    birthplace = db.Column(db.String(50))
    year_born = db.Column(db.Integer)
    year_died = db.Column(db.Integer)
    time_period = db.Column(db.String(10))
    image_path = db.Column(db.String(50))
    summary = db.Column(db.String(5000))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    documents = db.relationship("Document")

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

    def __repr__(self):
        return '<Philosopher: {}>'.format(self.name)

    @property
    def serialize(self):
        return {'id': self.id,
                'name': self.name.title(),
                'nationality': self.nationality.title(),
                'birthplace': self.birthplace.title(),
                'year_born': self.year_born,
                'year_died': self.year_died,
                'time_period': self.time_period.title(),
                'image_path': self.image_path,
                'summary': self.summary,
                'latitude': self.latitude,
                'longitude': self.longitude}


class Document(db.Model):
    __searchable__ = 'author'
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('philosophers.id'))
    author = db.Column(db.String(50))
    title = db.Column(db.String(60))
    year = db.Column(db.Integer)
    century = db.Column(db.Integer)
    text = db.Column(db.String(2000000))
    words = db.Column(db.Integer)
    url = db.Column(db.String(120))
    filepath = db.Column(db.String(50))

    def __init__(self, author, title, year, century, text, words, url, filepath):
        self.author = author
        self.title = title
        self.year = year
        self.century = century
        self.text = text
        self.words = words
        self.url = url
        self.filepath = filepath

    def __repr__(self):
        return '<Document Title: {}>'.format(self.title)

    @property
    def serialize(self):
        return {'id': self.id,
                'author_id': self.author_id,
                'author': self.author.title(),
                'title': self.title.title(),
                'year': self.year,
                'century': self.century,
                'text': self.text,
                'words': self.words,
                'url': self.url,
                'filepath': self.filepath}
