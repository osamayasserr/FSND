import sys
from datetime import datetime
from . import main
from flask import render_template, request, redirect, url_for, flash
from ..models import db, Artist, Venue, Show
from .forms import ShowForm, VenueForm, ArtistForm, DeleteArtist, DeleteVenue


@main.route('/')
def index():
    return render_template('pages/home.html')


@main.route('/venues')
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
        redirect(url_for('.index'))

    finally:
        db.session.close()


@main.route('/venues/search', methods=['POST'])
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
        redirect(url_for('.index'))

    finally:
        db.session.close()


@main.route('/venues/<int:venue_id>', methods=['GET', 'POST'])
def show_venue(venue_id):

    date = datetime.now()
    form = DeleteVenue()

    try:
        # If the user clicks the Delete Venue button
        if request.method == 'POST':

            # Delelte the venue from the database
            venue = Venue.query.get(venue_id)
            db.session.delete(venue)
            db.session.commit()

            # Flash a success message and redirect to homepage
            flash(f'Venue {venue.name} was successfully deleted!')
            return redirect(url_for('.index'))

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
        return redirect(url_for('.index'))

    finally:
        db.session.close()


@main.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@main.route('/venues/create', methods=['POST'])
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
        return redirect(url_for('.venues'))

    except Exception:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        return redirect(url_for('.index'))

    finally:
        db.session.close()


@main.route('/artists')
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
        return redirect(url_for('.index'))

    finally:
        db.session.close()


@main.route('/artists/search', methods=['POST'])
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
        redirect(url_for('.index'))

    finally:
        db.session.close()


@main.route('/artists/<int:artist_id>', methods=['GET', 'POST'])
def show_artist(artist_id):

    date = datetime.now()
    form = DeleteArtist()

    try:
        # If the user clicks the Delete Artist button
        if request.method == 'POST':
            artist = Artist.query.get(artist_id)
            db.session.delete(artist)
            db.session.commit()

            # Flash a success message and redirect to homepage
            flash(f'Artist {artist.name} was successfully deleted!')
            return redirect(url_for('.index'))

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

        return render_template('pages/show_artist.html', artist=artist_dict, form=form)

    except Exception:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        return redirect(url_for('.index'))

    finally:
        db.session.close()


@main.route('/artists/<int:artist_id>/edit', methods=['GET'])
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
        return redirect(url_for('.index'))
    finally:
        db.session.close()


@main.route('/artists/<int:artist_id>/edit', methods=['POST'])
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
        return redirect(url_for('.show_artist', artist_id=artist_id))

    except Exception:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        return redirect(url_for('.index'))

    finally:
        db.session.close()


@main.route('/venues/<int:venue_id>/edit', methods=['GET'])
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
        return redirect(url_for('.index'))
    finally:
        db.session.close()


@main.route('/venues/<int:venue_id>/edit', methods=['POST'])
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
        return redirect(url_for('.show_venue', venue_id=venue_id))

    except Exception:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        return redirect(url_for('.index'))

    finally:
        db.session.close()


@main.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@main.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
        # Get the submitted form data
        data = request.form
        name = data.get('name', '')
        city = data.get('city', '')
        state = data.get('state', '')
        phone = data.get('phone', '')
        genres = ','.join(data.getlist('genres'))
        facebook_link = data.get('facebook_link', '')

        # Create the venue and insert it into the DB
        artist = Artist(name, city, state, phone, genres, facebook_link)
        db.session.add(artist)
        db.session.commit()

        # On successful insert flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        return redirect(url_for('.artists'))

    except Exception:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        return redirect(url_for('.index'))

    finally:
        db.session.close()


@main.route('/shows')
def shows():
    data = []

    try:
        # Get all the shows
        shows = Show.query.all()

        # Loop over each show and generate its data
        for show in shows:
            show_dict = show.format_l()
            show_dict['artist_name'] = show.artist.name
            show_dict['artist_image_link'] = show.artist.image_link
            show_dict['venue_name'] = show.venue.name
            data.append(show_dict)

        return render_template('pages/shows.html', shows=data)

    except Exception:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        return redirect(url_for('.index'))

    finally:
        db.session.close()


@main.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@main.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        # Get the submitted form data
        data = request.form
        artist_id = data.get('artist_id')
        venue_id = data.get('venue_id')
        start_time = data.get('start_time')

        # Create the show and insert it to the DB
        show = Show(artist_id, venue_id, start_time)
        db.session.add(show)
        db.session.commit()

        # On successful insert flash success
        flash('Show was successfully listed!')
        return redirect(url_for('.shows'))

    except Exception:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        return redirect(url_for('.index'))

    finally:
        db.session.close()
