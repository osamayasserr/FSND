import os
from . import db


class Show(db.Model):
    __tablename__ = "shows"
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id', ondelete="CASCADE"), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id', ondelete="CASCADE"), primary_key=True)
    start_time = db.Column(db.DateTime, primary_key=True)

    def __init__(self, artist_id, venue_id, start_time):
        self.artist_id = artist_id
        self.venue_id = venue_id
        self.start_time = start_time

    def format_l(self):
        return {
            'artist_id': self.artist_id,
            'venue_id': self.venue_id,
            'start_time': str(self.start_time)
        }

    def format_s(self):
        return {
            'artist_id': self.artist_id,
            'start_time': str(self.start_time)
        }


class Venue(db.Model):
    __tablename__ = "venues"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120), default='Seeking talents!')
    image_link = db.Column(
        db.String(500),
        nullable=True,
        default=f"{os.getenv('DEFAULT_IMG')}")
    facebook_link = db.Column(db.String(120), nullable=True)
    artists = db.relationship(
        'Show',
        cascade='all, delete-orphan',
        backref=db.backref('venue', lazy=True)
    )

    def __init__(self, name, city, state, address, phone, genres, facebook_link):
        self.name = name
        self.city = city
        self.state = state
        self.address = address
        self.phone = phone
        self.genres = genres
        self.facebook_link = facebook_link

    def format_l(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'address': self.address,
            'phone': self.phone,
            'genres': str(self.genres).split(','),
            'website': self.website,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
        }

    def format_m(self):
        return {
            'venue_id': self.id,
            'venue_name': self.name,
            'venue_image_link': self.image_link
        }

    def format_s(self):
        return {
            'id': self.id,
            'name': self.name
        }


class Artist(db.Model):
    __tablename__ = "artists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120), default='Seeking venues!')
    image_link = db.Column(
        db.String(500),
        nullable=True,
        default=f"{os.getenv('DEFAULT_IMG')}")
    facebook_link = db.Column(db.String(120), nullable=True)
    shows = db.relationship(
        'Show',
        cascade='all, delete-orphan',
        backref=db.backref('artist', lazy=True))

    def __init__(self, name, city, state, phone, genres, facebook_link):
        self.name = name
        self.city = city
        self.state = state
        self.phone = phone
        self.genres = genres
        self.facebook_link = facebook_link

    def format_l(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'genres': str(self.genres).split(','),
            'website': self.website,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
        }

    def format_m(self):
        return {
            'artist_id': self.id,
            'artist_name': self.name,
            'artist_image_link': self.image_link
        }

    def format_s(self):
        return {
            'id': self.id,
            'name': self.name
        }
