from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Philosopher(Base):
    __tablename__ = 'philosophers'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    nationality = Column(String(50))
    birthplace = Column(String(50))
    year_born = Column(Integer)
    year_died = Column(Integer)
    time_period = Column(String(10))
    image_path = Column(String(50))
    summary = Column(String(5000))
    latitude = Column(Float)
    longitude = Column(Float)

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


class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('philosophers.id'))
    author = Column(String(50))
    title = Column(String(60))
    year = Column(Integer)
    century = Column(Integer)
    text = Column(String(2000000))
    words = Column(Integer)
    url = Column(String(120))
    filepath = Column(String(50))

    def __init__(self, author, year, century, text, words, url, filepath):
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
                'author': self.author,
                'year': self.year,
                'century': self.century,
                'text': self.text,
                'words': self.words,
                'url': self.url,
                'filepath': self.filepath}
