#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from datetime import datetime
import dateutil.parser
import babel
import sys
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for,
    abort
)
import logging
from logging import Formatter, FileHandler
from flask_migrate import Migrate
from flask_moment import Moment
from flask_wtf import FlaskForm as Form
from forms import *
from models import *
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db.init_app(app)
migrate = Migrate(app, db)

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
  error = False
  try: 
    venues = Venue.query.all()
    shows=Show.query.all()
    upcoming_shows=[]
    data=[]

    for show in shows:
      if show.start_time > datetime.now():
        upcoming_shows.append(show)
    

    for venue in venues:
      data.append({
          "city": venue.city,
          "state": venue.state,
          "venues": [{
              "id": venue.id,
              "name": venue.name,
              "num_upcoming_shows": len(upcoming_shows),
          }]
      })
    
  except:
    error = True
    print(sys.exc_info())

  if error:
    abort (400)
  else:
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  error = False
  try:
    search_term = request.form.get('search_term').lower()
    venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
    shows=Show.query.all()
    upcoming_shows=[]
    data=[]

    for ven in venues:
      for show in shows:
        if show.id == ven.show:
          if show.start_time > datetime.now():
            upcoming_shows.append(shows)

    response={
      "count": len(venues),
      "data": [{
        "venue": venues,
        "num_upcoming_shows": upcoming_shows
      }]
    }

  except:
    error = True
    print(sys.exc_info())

  if error:
    abort (400)
  else:
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  error = False
  try:
    venue = Venue.query.filter_by(id=venue_id).first()
    shows = Show.query.all()
    upcoming_shows=[]
    past_shows=[]
    data=[]

    for show in shows:
      if show.id == venue.shows:
        artist = Artist.query.filter(shows=show.id).first()
        if show.start_time > datetime.now():
          upcoming_shows.append({
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time)})
        else:
          past_shows.append({
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time)
          })

    data={
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
    }
  except:
    error = True
    print(sys.exc_info())

  if error:
    abort (400)
  else:
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
  error = False
  venue = Venue()
  form = VenueForm(request.form)

  try:
    form.populate_obj(venue)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
  finally:
    db.session.close()
  if error:
    abort (400)
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
    Venue.query.filter_by(venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
    error= True
  finally:
    db.session.close()
  if error:
    abort (400)
  return jsonify({ 'success': True })


#----------------------------------------------------------------------------#
#  Artists
#----------------------------------------------------------------------------#

@app.route('/artists')
def artists():
  error = False
  try:
    artists = Artist.query.all()
    data=[]

    for artist in artists:
      data.append({
        "id": artist.id,
        "name": artist.name
      })
  except:
    error = True
    print(sys.exc_info())

  if error:
    abort (400)
  else:
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  error = False
  try:
    search_term = request.form.get('search_term')
    artists = Artist.query.filter(Artist.name.ilike('%' + search_term.lower() + '%')).all()
    shows=Show.query.all()
    upcoming_shows=[]
    data=[]

    for artist in artists:
      for show in shows:
        if show.id == artist.shows and show.start_time > datetime.now():
          upcoming_shows.append(show)
      data.append({
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": upcoming_shows
      })

    response={
      "count": len(artists),
      "data": data
    }
  except:
    error = True
    print(sys.exc_info())

  if error:
    abort (400)
  else:
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  error = False
  try:
    artist = Artist.query.filter_by(id=artist_id).first()
    shows = Show.query.all()
    venue = Venue.query.join(Show, Show.venue_id == Venue.id).all()
    upcoming_shows=[]
    past_shows=[]

    for ven in venue:
      for show in shows:
        if artist.shows == show.id:
          if show.start_time > datetime.now():
            upcoming_shows.append({
              "venue_id": ven.id,
              "venue_name": ven.name,
              "venue_image_link": ven.image_link,
              "start_time": str(show.start_time)
            })
          else:
            if show.id == artist.shows:
              past_shows.append({
                "venue_id": ven.id,
                "venue_name": ven.name,
                "venue_image_link": ven.image_link,
                "start_time": str(show.start_time)
              })

    data= {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website_link,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
    }
  
  except:
    error = True
    print(sys.exc_info())

  if error:
    abort (400)
  else:
    return render_template('pages/show_artist.html', artist=data)

#----------------------------------------------------------------------------#
#  Update
#----------------------------------------------------------------------------#

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  error = False
  try:
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.image_link.data = artist.image_link
    form.facebook_link.data = artist.facebook_link
    form.website_link.data = artist.website_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

  except:
    error = True
    print(sys.exc_info())

  if error:
    abort (400)
  else:
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  artist_data = request.form
  form =  ArtistForm(artist_data)

  try:
    artist = Artist.query.get(artist_id)
    artist.name=form.name.data
    artist.city=form.city.data
    artist.state=form.state.data
    artist.phone=form.phone.data
    artist.genres=form.genres.data
    artist.image_link=form.image_link.data
    artist.facebook_link=form.facebook_link.data
    artist.website_link=form.website_link.data
    artist.seeking_venue=form.seeking_venue.data
    artist.seeking_description=form.seeking_description.data
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Artist ' + data.name + ' could not upadate.')
  finally:
    db.session.close()
  if error:
    abort (400)

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  error = False
  
  try:
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.image_link.data = venue.image_link
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.website_link.data = venue.website_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
 
  except:
    error = True
    print(sys.exc_info())

  if error:
    abort (400)
  else:
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  venue_data = request.form
  form = VenueForm(venue_data)

  try:
    venue = Venue.query.get(venue_id)
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.genres = form.genres.data
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    venue.website_link = form.website_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Venue ' + data.name + ' could not upadate.')
  finally:
    db.session.close()
  if error:
    abort (400)
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
  error = False
  artist = Artist()
  form = VenueForm(request.form)

  try:
    form.populate_obj(artist)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  finally:
    db.session.close()
  if error:
    abort (400)

  return render_template('pages/home.html')

#----------------------------------------------------------------------------#
#  Shows
#----------------------------------------------------------------------------#

@app.route('/shows')
def shows():
  error = False
  data = []
  try: 
    shows = Show.query.join(Venue).join(Artist).all()

    for show in shows:
      data.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": str(show.start_time)
      })

  except:
    error = True
    print(sys.exc_info())

  if error:
    abort (400)
  else:
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  show = Show()
  form = ShowForm(request.form)

  try:
    form.populate_obj(show)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  if error:
    abort (400)

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
