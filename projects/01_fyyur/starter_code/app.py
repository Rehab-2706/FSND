#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from datetime import datetime
import dateutil.parser
import babel
from flask import (render_template, request, Response, flash, redirect, url_for)
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)

    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"

    return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#----------------------------------------------------------------------------#
#  Venues
#----------------------------------------------------------------------------#

@app.route('/venues')
def venues():
      # TODO: replace with real venues data.. Done
      #     num_shows should be aggregated based on number of upcoming shows per venue.. Done

    venues_city_location = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state).all()
    data = []

    for venue_city_location in venues_city_location:
        venues = Venue.query.filter(Venue.city==venue_city_location[0] and Venue.state==venue_city_location[1]).all()
        upcoming_shows_query = db.session.query(Show).join(Venue).filter(Venue.city==venue_city_location[0] and Venue.state==venue_city_location[1]).all()
        data.append({
            "city": venue_city_location[0],
            "state": venue_city_location[1],
            "venues": [{
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(upcoming_shows_query),
            } for venue in venues]
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.. Done
    # seach for Hop should return "The Musical Hop".. Done
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee".. Done
    search_term = request.form.get('search_term').lower()
    target_venue = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
    results = {
      "count": len(target_venue),
      "data": [{
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(db.session.query(Show).join(Venue). \
          filter(Venue.id==venue.id).filter(Show.start_time > datetime.now()).all()),
      } for venue in target_venue]
    }

    return render_template('pages/search_venues.html', results=results, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id.. Done
    # TODO: replace with real venue data from the venues table, using venue_id.. Done
    venue = Venue.query.filter_by(id=venue_id).first()
    past_shows_query = db.session.query(Show).join(Venue).filter(Venue.id == venue_id).filter(Show.start_time < datetime.now()).all()
    upcoming_shows_query = db.session.query(Show).join(Venue).filter(Venue.id == venue_id).filter(Show.start_time > datetime.now()).all()

    past_shows = []
    upcoming_shows = []

    for show in past_shows_query:
        past_shows.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": str(show.start_time)
        })

    for show in upcoming_shows_query:
        upcoming_shows.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": str(show.start_time)
        })

    data = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website_link,
      "image_link": venue.image_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows_query),
      "upcoming_shows_count": len(upcoming_shows_query)
    }
    return render_template('pages/show_venue.html', venue=data)

#----------------------------------------------------------------------------#
#  Create Venue
#----------------------------------------------------------------------------#

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()

  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead.. Done
    # TODO: modify data to be the data object returned from db insertion.. Done

    form = VenueForm(request.form)

    try:
        venue = Venue()
        form.populate_obj(venue)
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + venue.name + ' was successfully listed!')

    except Exception:
        flash('An error occurred. Venue ' + request.form.get('name') + ' could not be listed.')
        db.session.rollback()

    finally:
        db.session.close()
  # on successful db insert, flash success.. Done
  #flash('Venue ' + request.form['name'] + ' was successfully listed!').. Done
  # TODO: on unsuccessful db insert, flash an error instead.. Done
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.').. Done
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/.. Done
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using.. Done
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.. Done

    venue = Venue.query.filter_by(id=venue_id).one()

    try:
        venue = Venue.query.filter_by(id=venue_id).one()
        db.session.delete(venue)
        db.session.commit()
        flash("Venue deleted successfully!")

    except Exception:
        db.session.rollback()
        flash("Venue was not deleted. Something went wrong!")

    finally:
        db.session.close()

    return redirect(url_for('index'))

#----------------------------------------------------------------------------#
#  Artists
#----------------------------------------------------------------------------#

@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database.. Done
    artists = Artist.query.all()
    print(artists)

    data = []

    for artist in artists:
        data.append({
          "id": artist.id,
          "name": artist.name,
        })

    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.. Done
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".. Done
    # search for "band" should return "The Wild Sax Band".. Done
    search_term = request.form.get('search_term').lower()

    target_artist = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()

    results = {
      "count": len(target_artist),
      "data": [{
          "id": artist.id,
          "name": artist.name,
          "num_upcoming_shows": len(db.session.query(Show).join(Artist). \
          filter(Artist.id==artist.id).filter(Show.start_time > datetime.now()).all()),
      } for artist in target_artist]
    }

    return render_template('pages/search_artists.html', results=results, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id.. Done
    # TODO: replace with real artist data from the artist table, using artist_id.. Done
    artist = Artist.query.filter_by(id=artist_id).first()

    past_shows_query = db.session.query(Show).join(Artist).filter(Artist.id == artist_id).filter(Show.start_time < datetime.now()).all()
    upcoming_shows_query = db.session.query(Show).join(Artist).filter(Artist.id == artist_id).filter(Show.start_time > datetime.now()).all()

    past_shows = []
    upcoming_shows = []

    for show in past_shows_query:
        past_shows.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": str(show.start_time)
        })

    for show in upcoming_shows_query:
        upcoming_shows.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": str(show.start_time)
        })

    artist_details = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website_link,
      "image_link": artist.image_link,
      "facebook_link": artist.facebook_link,
      "seeking_venues": artist.seeking_venues,
      "seeking_description": artist.seeking_description,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows_query),
      "upcoming_shows_count": len(upcoming_shows_query)
    }

    return render_template('pages/show_artist.html', artist=artist_details)

#----------------------------------------------------------------------------#
#  Update
#----------------------------------------------------------------------------#

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist_data = request.form
    form =  ArtistForm(artist_details)

    try:
        artist = Artist.query.get(artist_id)
        artist.name = artist_data.get('name')
        artist.city = artist_data.get('city')
        artist.state = artist_data.get('state')
        artist.phone = artist_data.get('phone')
        artist.genres = artist_data.getlist('genres')
        artist.image_link = artist_data.get('image_link')
        artist.facebook_link = artist_data.get('facebook_link')
        artist.website_link = artist_data.get('website_link')
        artist.seeking_venues = artist_data.get('seeking_venues')
        artist.seeking_description = artist_data.get('seeking_description')
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully updated!')

    except Exception:
        db.session.rollback()
        flash('Artist ' + request.form['name'] + ' was not updated. Something went wrong.')

    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website_link
    form.facebook_link.data = artist.facebook_link
    form.seeking_venues.data = artist.seeking_venues
    form.seeking_description.data = artist.seeking_description

  # TODO: populate form with fields from artist with ID <artist_id>.. Done
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website_link.data = venue.website_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

  # TODO: populate form with values from venue with ID <venue_id>.. Done
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing.. Done
    # venue record with ID <venue_id> using the new attributes.. Done
    venue_data = request.form
    form = VenueForm(venue_data)

    try:
        venue = Venue.query.get(venue_id)
        venue.name = venue_data.get("name")
        venue.city = venue_data.get("city")
        venue.state = venue_data.get("state")
        venue.address = venue_data.get("address")
        venue.phone = venue_data.get("phone")
        venue.genres = venue_data.getlist("genres")
        venue.facebook_link = venue_data.get("facebook_link")
        venue.image_link = venue_data.get("image_link")
        venue.website_link = venue_data.get("website_link")
        venue.seeking_talent = venue_data.get("seeking_talent")
        venue.seeking_description = venue_data.get("seeking_description")
        db.session.commit()
        flash('Venue ' + venue_data.get('name') + ' was successfully updated!')

    except Exception:
        db.session.rollback()
        flash('Venue ' + venue_data.get('name') + ' was not updated. Something went wrong.')

    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#----------------------------------------------------------------------------#
#  Create Artist
#----------------------------------------------------------------------------#

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form.. Done
    # TODO: insert form data as a new Venue record in the db, instead.. Done
    # TODO: modify data to be the data object returned from db insertion.. Done
    form = ArtistForm(request.form)

    try:
        artist = Artist()
        form.populate_obj(artist)
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + artist.name + ' was successfully listed!')

    except Exception:
        flash('An error occurred. Artist ' + request.form.get('name') + ' could not be listed.')
        db.session.rollback()

    finally:
        db.session.close()
    # on successful db insert, flash success.. Done
    #flash('Artist ' + request.form['name'] + ' was successfully listed!').. Done
    # TODO: on unsuccessful db insert, flash an error instead.. Done
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.').. Done
    return render_template('pages/home.html')

#----------------------------------------------------------------------------#
#  Shows
#----------------------------------------------------------------------------#

@app.route('/shows')
def shows():
    # displays list of shows at /shows.. Done
    # TODO: replace with real venues data.. Done
    #       num_shows should be aggregated based on number of upcoming shows per venue.. Done
    show_data = []
    shows = Show.query.order_by('venue_id').all()

    for show in shows:
        show_data.append({
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
        })
    # on successful db insert, flash success.. Done
    #flash('Show was successfully listed!').. Done
    # TODO: on unsuccessful db insert, flash an error instead.. Done
    # e.g., flash('An error occurred. Show could not be listed.').. Done
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/.. Done
    return render_template('pages/shows.html', shows=show_data)


@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)

    try:
        show = Show()
        form.populate_obj(show)
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')

    except Exception:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')

    finally:
        db.session.close()

    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

@app.errorhandler(401)
def unauthorized_error(error):
    return render_template('errors/500.html'), 401

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
