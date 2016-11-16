from database import db
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship


class Philosopher(db.Model):
    __tablename__ = 'philosopher'

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
    __tablename__ = 'document'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('philosopher.id'))
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

class CurrentTopics(db.Model):
    __tablename__ = 'current_topics'

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    first_id = db.Column(db.Integer)
    first_title = db.Column(db.String(50))
    first_prob = db.Column(db.Float)
    second_id = db.Column(db.Integer)
    second_title = db.Column(db.String(50))
    second_prob = db.Column(db.Float)
    third_id = db.Column(db.Integer)
    third_title = db.Column(db.String(50))
    third_prob = db.Column(db.Float)
    fourth_id = db.Column(db.Integer)
    fourth_title = db.Column(db.String(50))
    fourth_prob = db.Column(db.Float)
    fifth_id = db.Column(db.Integer)
    fifth_title = db.Column(db.String(50))
    fifth_prob = db.Column(db.Float)

    def __init__(self, year, first_id, first_title, first_prob, second_id, second_title, second_prob, \
                 third_id, third_title, third_prob, fourth_id, fourth_title, fourth_prob, \
                 fifth_id, fifth_title, fifth_prob):
        self.year = year
        self.first_id = first_id
        self.first_title = first_title
        self.first_prob = first_prob
        self.second_id = second_id
        self.second_title = second_title
        self.second_prob = second_prob
        self.third_id = third_id
        self.third_title = third_title
        self.third_prob = third_prob
        self.fourth_id = fourth_id
        self.fourth_title = fourth_title
        self.fourth_prob = fourth_prob
        self.fifth_id = fifth_id
        self.fifth_title = fifth_title
        self.fifth_prob = fifth_prob

    @property
    def serialize(self):
        return {'year': self.year,
                'first_id': self.first_id,
                'first_title': self.first_title,
                'first_prob': self.first_prob,
                'second_id': self.second_id,
                'second_title': self.second_title,
                'second_prob': self.second_prob,
                'third_id': self.third_id,
                'third_title': self.third_title,
                'third_prob': self.third_prob,
                'fourth_id': self.fourth_id,
                'fourth_title': self.fourth_title,
                'fourth_prob': self.fourth_prob,
                'fifth_id': self.fifth_id,
                'fifth_title': self.fifth_title,
                'fifth_prob': self.fifth_prob}
