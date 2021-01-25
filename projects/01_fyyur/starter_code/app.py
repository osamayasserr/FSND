# Imports
import os
import sys
import json
import dateutil.parser
import babel
import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask.logging import create_logger
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

# Flask app initialization & configuration
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
log = create_logger(app)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Show(db.Model):
    __tablename__ = "shows"
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id'), primary_key=True)
    start_time = db.Column(db.DateTime, primary_key=True)

    def format_s(self):
        return {
            'artist_id': self.artist_id,
            'start_time': self.start_time
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
        'Artist', secondary='shows',
        backref=db.backref('venues', lazy=True)
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


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------#
# Shell Context.
#----------------------------------------------------------------------------#

@app.shell_context_processor
def add_shell_context():
    return dict(db=db, Artist=Artist, Venue=Venue, Show=Show)

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

    data = []
    date = datetime.now()

    try:
        # Get all the unique locations (city, state) of venues
        locations = Venue.query.with_entities(
            Venue.city.distinct(), Venue.state).all()

        # Loop over all the locations & create a data_dict for each one
        for location in locations:
            data_dict = {}
            city, state = location
            data_dict['city'] = city
            data_dict['state'] = state

            # Get all venues in location
            venue_list = []
            venues = Venue.query.filter(Venue.city == city).all()

            # Loop over all venues in that location & create a venue_dict for each one
            for venue in venues:
                venue_id, venue_dict = venue.id, venue.format_l()

                # Get the number of upcoming shows for that venue
                venue_dict['num_upcoming_shows'] = Show.query.filter(
                    Show.venue_id == venue_id,
                    Show.start_time > date).count()
                venue_list.append(venue_dict)

            data_dict['venues'] = venue_list
            data.append(data_dict)

        return render_template('pages/venues.html', areas=data)

    except Exception:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        redirect(url_for('index'))

    finally:
        db.session.close()


@app.route('/venues/search', methods=['POST'])
def search_venues():

    data = {}
    date = datetime.now()

    try:
        # Get the search term and query the database using LIKE
        search_term = request.form.get('search_term', '')
        venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

        data['count'] = len(venues)
        data['data'] = []

        # Loop over the resulting venues
        for venue in venues:
            venue_id, venue_dict = venue.id, venue.format_s()

            # Get the number of upcoming shows for that venue
            venue_dict['num_upcoming_shows'] = Show.query.filter(
                Show.venue_id == venue_id,
                Show.start_time > date).count()

            data['data'].append(venue_dict)

        return render_template('pages/search_venues.html',
                               results=data, search_term=search_term)

    except Exception:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        redirect(url_for('index'))

    finally:
        db.session.close()


@ app.route('/venues/<int:venue_id>', methods=['GET', 'POST'])
def show_venue(venue_id):

    date = datetime.now()
    form = DeleteVenue()

    try:
        # If the user clicks the Delete Venue button
        if form.validate_on_submit():

            # Delelte the venue from the database
            venue = Venue.query.get(venue_id)
            db.session.delete(venue)
            db.session.commit()

            # Flash a success message and redirect to homepage
            flash(f'Venue {venue.name} was successfully deleted!')
            return redirect(url_for('index'))

        # Get the venue with id = venue_id & create a data dict
        venue_dict = Venue.query.get(venue_id).format_l()
        venue_dict['upcoming_shows'] = []
        venue_dict['past_shows'] = []

        # Get the upcoming shows for that venue
        upcoming_shows = Show.query.filter(
            Show.venue_id == venue_id,
            Show.start_time > date).all()

        # Get the needed data from all upcoming shows
        for show in upcoming_shows:
            artist_id = show.artist_id
            artist_dict = Artist.query.get(artist_id).format_m()
            artist_dict['start_time'] = str(show.start_time)
            venue_dict['upcoming_shows'].append(artist_dict)

        venue_dict['upcoming_shows_count'] = len(upcoming_shows)

        # Get the past shows for that venue
        past_shows = Show.query.filter(
            Show.venue_id == venue_id,
            Show.start_time < date).all()

        # Get the needed data from past shows
        for show in past_shows:
            artist_id = show.artist_id
            artist_dict = Artist.query.get(artist_id).format_m()
            artist_dict['start_time'] = str(show.start_time)
            venue_dict['past_shows'].append(artist_dict)

        venue_dict['past_shows_count'] = len(past_shows)

        return render_template('pages/show_venue.html', venue=venue_dict, form=form)

    except Exception:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        return redirect(url_for('index'))

    finally:
        db.session.close()
#  Create Venue
#  ----------------------------------------------------------------


@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        # Get the submitted form data
        data = request.form
        name = data.get('name', '')
        city = data.get('city', '')
        state = data.get('state', '')
        address = data.get('address', '')
        phone = data.get('phone', '')
        genres = ','.join(data.getlist('genres'))
        facebook_link = data.get('facebook_link', '')

        # Create the venue and insert it into the DB
        venue = Venue(name, city, state, address, phone, genres, facebook_link)
        db.session.add(venue)
        db.session.commit()

        # On successful insert flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return redirect(url_for('index'))

    except Exception:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        return redirect(url_for('index'))

    finally:
        db.session.close()

#  Artists
#  ----------------------------------------------------------------


@ app.route('/artists')
def artists():

    data = []

    try:
        # Get all the artists data
        artists = Artist.query.all()
        for artist in artists:
            data.append(artist.format_s())

        return render_template('pages/artists.html', artists=data)

    except Exception:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        return redirect(url_for('index'))

    finally:
        db.session.close()


@ app.route('/artists/search', methods=['POST'])
def search_artists():

    data = {}
    date = datetime.now()

    try:
        # Get the search term and query the database using LIKE
        search_term = request.form.get('search_term', '')
        venues = Artist.query.filter(
            Artist.name.ilike(f'%{search_term}%')).all()

        data['count'] = len(venues)
        data['data'] = []

        # Loop over the resulting venues
        for venue in venues:
            venue_id, venue_dict = venue.id, venue.format_s()

            # Get the number of upcoming shows for that venue
            venue_dict['num_upcoming_shows'] = Show.query.filter(
                Show.venue_id == venue_id,
                Show.start_time > date).count()

            data['data'].append(venue_dict)

        return render_template('pages/search_venues.html',
                               results=data, search_term=search_term)

    except Exception:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        redirect(url_for('index'))

    finally:
        db.session.close()


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    date = datetime.now()

    try:
        # Get the artist with id = artist_id & create a data dict
        artist_dict = Artist.query.get(artist_id).format_l()
        artist_dict['upcoming_shows'] = []
        artist_dict['past_shows'] = []

        # Get the upcoming shows for that artist
        upcoming_shows = Show.query.filter(
            Show.artist_id == artist_id,
            Show.start_time > date).all()

        # Get the needed data from all upcoming shows
        for show in upcoming_shows:
            venue_id = show.venue_id
            venue_dict = Venue.query.get(venue_id).format_m()
            venue_dict['start_time'] = str(show.start_time)
            artist_dict['upcoming_shows'].append(venue_dict)

        artist_dict['upcoming_shows_count'] = len(upcoming_shows)

        # Get the past shows for that artist
        past_shows = Show.query.filter(
            Show.artist_id == artist_id,
            Show.start_time < date).all()

        # Get the needed data from past shows
        for show in past_shows:
            venue_id = show.venue_id
            venue_dict = Venue.query.get(venue_id).format_m()
            venue_dict['start_time'] = str(show.start_time)
            artist_dict['past_shows'].append(venue_dict)

        artist_dict['past_shows_count'] = len(past_shows)

        return render_template('pages/show_artist.html', artist=artist_dict)

    except Exception:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        return redirect(url_for('index'))

    finally:
        db.session.close()

#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

    form = ArtistForm()

    try:
        # Get the artist's data
        artist = Artist.query.get(artist_id).format_l()
        return render_template('forms/edit_artist.html', form=form, artist=artist)

    except Exception:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        return redirect(url_for('index'))
    finally:
        db.session.close()


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        # Get the submitted form data
        data = request.form
        name = data.get('name', '')
        city = data.get('city', '')
        state = data.get('state', '')
        phone = data.get('phone', '')
        genres = ','.join(data.getlist('genres'))
        facebook_link = data.get('facebook_link', '')

        # Get the artist and update its data
        artist = Artist.query.get(artist_id)
        artist.name = name
        artist.city = city
        artist.state = state
        artist.phone = phone
        artist.genres = genres
        artist.facebook_link = facebook_link
        db.session.add(artist)
        db.session.commit()

        # On successful insert flash success
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
        return redirect(url_for('show_artist', artist_id=artist_id))

    except Exception:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        return redirect(url_for('index'))

    finally:
        db.session.close()


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

    form = VenueForm()

    try:
        # Get the venue's data
        venue = Venue.query.get(venue_id).format_l()
        return render_template('forms/edit_venue.html', form=form, venue=venue)

    except Exception:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        return redirect(url_for('index'))
    finally:
        db.session.close()


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        # Get the submitted form data
        data = request.form
        name = data.get('name', '')
        city = data.get('city', '')
        state = data.get('state', '')
        address = data.get('address', '')
        phone = data.get('phone', '')
        genres = ','.join(data.getlist('genres'))
        facebook_link = data.get('facebook_link', '')

        # Get the venue and update its data
        venue = Venue.query.get(venue_id)
        venue.name = name
        venue.city = city
        venue.state = state
        venue.phone = phone
        venue.genres = genres
        venue.facebook_link = facebook_link
        db.session.add(venue)
        db.session.commit()

        # On successful insert flash success
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
        return redirect(url_for('show_venue', venue_id=venue_id))

    except Exception:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        return redirect(url_for('index'))

    finally:
        db.session.close()

#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = [{
        "venue_id": 1,
        "venue_name": "The Musical Hop",
        "artist_id": 4,
        "artist_name": "Guns N Petals",
        "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "start_time": "2019-05-21T21:30:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 5,
        "artist_name": "Matt Quevedo",
        "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "start_time": "2019-06-15T23:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-01T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-08T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-15T20:00:00.000Z"
    }]
    return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    log.setLevel(log.INFO)
    file_handler.setLevel(log.INFO)
    log.addHandler(file_handler)
    log.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
'''
if __name__ == '__main__':
    app.run()
'''

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
