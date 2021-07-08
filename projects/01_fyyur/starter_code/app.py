#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
import sys
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database.. Done


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(250))
    shows = db.relationship('Show', backref='venue', cascade="all,delete", lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate.. Done

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venues = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(250))
    shows = db.relationship('Show', backref='artist', cascade="all,delete", lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate.. Done

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer , db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer , db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime , nullable=False)

    def __repr__(self):
      return f'<Show : {self.id}>'

  # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.. Done


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


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.. Done
  #       num_shows should be aggregated based on number of upcoming shows per venue.. Done
  data = []
  venues = Venue.query.all()
  venue_details = set()
  
  for venue in venues:
    venue_details.add((venue.city, venue.state))

  for venue_city_state in venue_details:
    data.append({
      "city": venue_city_state[0],
      "state": venue_city_state[1],
      "venues": []})

  for venue in venues:
    num_upcoming_shows = Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > datetime.now()).all()

    for venue_detail in data:
      if venue.city == venue_detail['city'] and venue.state == venue_detail['state']:
        venue_detail['venues'].append({
          "id": venue.id, 
          "name": venue.name,
          "num_upcoming_shows": len(num_upcoming_shows)
        })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.. Done
  # seach for Hop should return "The Musical Hop".. Done
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee".. Done
  data = []
  count_venue = 0

  search_term = request.form.get('search_term', '').lower() 
  venues = Venue.query.all()

  for venue in venues:
    target_venue = venue.name.lower()
    if target_venue.find(search_term) != -1:
      data.append(venue)
      count_venue += 1
    
  response = { 
    "count_venue": count_venue, 
    "data": data 
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id.. Done
  # TODO: replace with real venue data from the venues table, using venue_id.. Done
  num_upcoming_shows = []
  num_past_shows = []

  venue = Venue.query.get(venue_id)
  shows = Show.query.filter_by(venue_id = venue_id).all()

  for show in shows:
    if show.start_time > datetime.now():
      num_upcoming_shows.append({
        "artist_id": show.artist_id,
        "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
        "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
        "start_time": format_datetime(str(show.start_time))
      })
    else:
      num_past_shows.append({
        "artist_id": show.artist_id,
        "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
        "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
        "start_time": format_datetime(str(show.start_time))
      })

  venue_details = {
    "id": venue.id,
    "name": venue.name,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "genres": venue.genres,
    "address": venue.address,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "image_link": venue.image_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "past_shows": num_past_shows,
    "upcoming_shows": num_upcoming_shows,
    "past_shows_count": len(num_past_shows),
    "upcoming_shows_count": len(num_upcoming_shows)
  }
  return render_template('pages/show_venue.html', venue=venue_details)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead.. Done
  # TODO: modify data to be the data object returned from db insertion.. Done
  try:
    seeking_talent = request.form.get('seeking_talent', None)
    venue = Venue(
      name = request.form['name'],
      address = request.form['address'],
      city = request.form['city'],
      state = request.form['state'],
      phone = request.form['phone'],
      genres = request.form.getlist('genres'),
      facebook_link = request.form['facebook_link'],
      image_link = request.form['image_link'],
      website = request.form['website'],
      seeking_talent = True if seeking_talent != None else False,
      seeking_description = request.form['seeking_description']
    )
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    print(sys.exc_info())

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
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue + ' was successfully deleted!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. '+ sys.exc_info()[0]+'. Venue ' + venue + ' could not be deleted.')
  finally:
    db.session.close()

  return render_template('layouts/main.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database.. Done
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.. Done
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".. Done
  # search for "band" should return "The Wild Sax Band".. Done
  data = []
  count = 0

  search_term = request.form.get('search_term', '').lower()
  artists = Artist.query.all() 
  
  for artist in artists:
    target_artist = artist.name.lower()
    if (target_artist.find(search_term) != -1):
      data.append(artist)
      count += 1

  response = {
   "data" : data,
   "count" : count
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id.. Done
  # TODO: replace with real artist data from the artist table, using artist_id.. Done
  num_upcoming_shows = []
  num_past_shows = []

  artist = Artist.query.get(artist_id)
  shows = Show.query.filter_by(artist_id=artist_id)
  
  for show in shows:
    if show.start_time < datetime.now():
      num_past_shows.append({
        "artist_id": show.artist_id,
        "venue_id" : show.venue_id,
        "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
        "venue_image_link": Venue.query.filter_by(id=show.venue_id).first().image_link,
        "start_time": format_datetime(str(show.start_time))
      })
    else:
      num_upcoming_shows.append({
        "artist_id": show.artist_id,
        "venue_id" : show.venue_id,
        "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
        "venue_image_link": Venue.query.filter_by(id=show.venue_id).first().image_link,
        "start_time": format_datetime(str(show.start_time))
      })
  
  data = {
    "id": artist.id,
    "name": artist.name,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "genres": artist.genres,
    "website" : artist.website,
    "image_link": artist.image_link,
    "facebook_link": artist.facebook_link,
    "seeking_venues": artist.seeking_venues,
    "seeking_description": artist.seeking_description,
    "past_shows": num_past_shows,
    "upcoming_shows": num_upcoming_shows,
    "past_shows_count": len(num_past_shows),
    "upcoming_shows_count": len(num_upcoming_shows)
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
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
  form.website.data = artist.website
  form.facebook_link.data = artist.facebook_link
  form.seeking_venues.data = artist.seeking_venues
  form.seeking_description.data = artist.seeking_description

  # TODO: populate form with fields from artist with ID <artist_id>.. Done
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing.. Done
  # artist record with ID <artist_id> using the new attributes.. Done
  artist = Artist.query.get(artist_id)

  try:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = ','.join(request.form.getlist('genres'))
    artist.facebook_link = request.form['facebook_link']
    artist.image_link = request.form['image_link']
    artist.website = request.form['website']
    seeking_venues = request.form.get('seeking_venues', None)
    artist.seeking_venues = True if seeking_venues != None else False
    artist.seeking_description = request.form['seeking_description']
    
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
    print(sys.exc_info())

  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

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
  form.website.data = venue.website
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description

  # TODO: populate form with values from venue with ID <venue_id>.. Done
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing.. Done
  # venue record with ID <venue_id> using the new attributes.. Done
  venue = Venue.query.get(venue_id)

  try:
    venue.name = request.form['name']
    venue.genres = ','.join(request.form.getlist('genres'))
    venue.address = request.form['address']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.facebook_link = request.form['facebook_link']
    venue.image_link = request.form['image_link']
    venue.website = request.form['website']
    seeking_talent = request.form.get('seeking_talent', None)
    venue.seeking_talent = True if seeking_talent != None else False
    venue.seeking_description = request.form['seeking_description']
    
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
    print(sys.exc_info())

  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form.. Done
  # TODO: insert form data as a new Venue record in the db, instead.. Done
  # TODO: modify data to be the data object returned from db insertion.. Done
  try:
    seeking_venues = request.form.get('seeking_venues', None)

    artist = Artist(  
      name = request.form['name'],
      genres = request.form.getlist('genres'),
      city = request.form['city'],
      state = request.form['state'],
      phone = request.form['phone'],
      website = request.form['website'],
      facebook_link = request.form['facebook_link'],
      seeking_venues = True if seeking_venues != None else False,
      seeking_description = request.form['seeking_description'],
      image_link = request.form['image_link']
    )

    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    print(sys.exc_info())

  finally:
    db.session.close()

  # on successful db insert, flash success.. Done
  #flash('Artist ' + request.form['name'] + ' was successfully listed!').. Done
  # TODO: on unsuccessful db insert, flash an error instead.. Done
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.').. Done
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows.. Done
  # TODO: replace with real venues data.. Done
  #       num_shows should be aggregated based on number of upcoming shows per venue.. Done
  data = []
  shows = Show.query.all()

  for show in shows: 
    data.append({
      "venue_id" : show.venue_id,
      "venue_name": Venue.query.filter_by(id=show.venue_id).first().name, 
      "artist_id": show.artist_id, 
      "artist_name": Artist.query.filter_by(id=show.artist_id).first().name, 
      "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
      "start_time": format_datetime(str(show.start_time))
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form.. Done
  # TODO: insert form data as a new Show record in the db, instead.. Done
  try:
    show = Show(
      venue_id = request.form['venue_id'],
      artist_id = request.form['artist_id'],
      start_time = request.form['start_time']
    )

    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')

  except:
    db.session.rollback()
    flash('An error occurred, the show could not be listed.')
    print(sys.exc_info())

  finally:
    db.session.close()

  # on successful db insert, flash success.. Done
  #flash('Show was successfully listed!').. Done
  # TODO: on unsuccessful db insert, flash an error instead.. Done
  # e.g., flash('An error occurred. Show could not be listed.').. Done
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/.. Done
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


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
