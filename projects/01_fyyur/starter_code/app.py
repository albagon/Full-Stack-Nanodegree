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
from logging import Formatter, FileHandler
from flask_wtf import Form
from datetime import datetime
from forms import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
# DONE
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

venue_artist = db.Table('venue_artist',
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(500))
    artists = db.relationship('Artist', secondary=venue_artist,
        backref=db.backref('venues', lazy=True))
    shows = db.relationship('Show', backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # DONE

class Artist(db.Model):
    __tablename__ = 'Artist'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # DONE
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def dictionary(self):
      return {
        'id': self.id,
        'name': self.name,
        'genres': self.genres,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'website': self.website,
        'image_link': self.image_link,
        'facebook_link': self.facebook_link,
        'seeking_venue': self.seeking_venue,
        'seeking_description': self.seeking_description
      }

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# DONE

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'),
        nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),
        nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Utilities.
#----------------------------------------------------------------------------#

# This function takes a list of artist show objects and gives them the right
# format so that they can be displayed in the template.
# Returns a new dictionary with the formatted data.
def artist_show_list_to_dict(show_list):
  shows_dict = []
  for show in show_list:
    show_d = show.__dict__
    show_d['start_time'] = str(show_d['start_time'])
    show_d['venue_name'] = show.venue.name
    show_d['venue_image_link'] = show.venue.image_link
    shows_dict.append(show_d)
  return shows_dict

# This function takes a list of venue show objects and gives them the right
# format so that they can be displayed in the template.
# Returns a new dictionary with the formatted data.
def venue_show_list_to_dict(show_list):
  shows_dict = []
  for show in show_list:
    show_d = show.__dict__
    artist = Artist.query.filter(Artist.id == show_d['artist_id']).first()
    artist_d = artist.__dict__
    show_d['artist_name'] = artist_d['name']
    show_d['artist_image_link'] = artist_d['image_link']
    show_d['start_time'] = str(show_d['start_time'])
    shows_dict.append(show_d)
  return shows_dict

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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # DONE
  venues = Venue.query.order_by(Venue.city, Venue.state).all()

  data = []
  last_city = None
  last_state = None
  today = datetime.today()
  location = None
  for venue in venues:
    venue_dict = {
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': Show.query.filter(Show.venue_id == venue.id, Show.start_time >= today).count()
    }
    if venue.city == last_city and venue.state == last_state:
      location['venues'].append(venue_dict)
    else:
      if location is not None:
        data.append(location)
      location = {}
      location['city'] = venue.city
      location['state'] = venue.state
      location['venues'] = [venue_dict]
    last_city = venue.city
    last_state = venue.state
  data.append(location)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # search for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # DONE
  search_term=request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
  data = []
  for venue in venues:
    venue_d = venue.__dict__
    data.append({
      "id": venue_d['id'],
      "name": venue_d['name'],
      "num_upcoming_shows": Show.query.filter(Show.id == venue_d['id']).count()
    })
  response={
    "count": len(venues),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # DONE
  venue = Venue.query.get(venue_id)
  venue_dict = venue.__dict__
  today = datetime.today()

  upcoming_shows = Show.query.filter(Show.start_time >= today, Show.venue_id == venue_id).all()
  upcoming_shows_dict = venue_show_list_to_dict(upcoming_shows)
  venue_dict['upcoming_shows'] = upcoming_shows_dict
  venue_dict['upcoming_shows_count'] = len(upcoming_shows_dict)

  past_shows = Show.query.filter(Show.start_time < today, Show.venue_id == venue_id).all()
  past_shows_dict = venue_show_list_to_dict(past_shows)
  venue_dict['past_shows'] = past_shows_dict
  venue_dict['past_shows_count'] = len(past_shows_dict)

  return render_template('pages/show_venue.html', venue=venue_dict)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # DONE
  # TODO: modify data to be the data object returned from db insertion
  # DONE
  error = False
  bool_seeking_talent = True
  body = {}
  try:
    form = request.form
    genres_list = request.form.getlist('genres')
    if form['seeking_talent'] == 'Yes':
      bool_seeking_talent = True
    else:
      bool_seeking_talent = False
    venue = Venue(
      name= form['name'],
      genres = genres_list,
      address = form['address'],
      city = form['city'],
      state = form['state'],
      phone = form['phone'],
      facebook_link = form['facebook_link'],
      website = form['website'],
      image_link = form['image_link'],
      seeking_talent = bool_seeking_talent,
      seeking_description = form['seeking_description']
    )
    db.session.add(venue)
    db.session.commit()
    body['name'] = venue.name
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if not error:
      # on successful db insert, flash success
      flash('Venue ' + body['name'] + ' was successfully listed!')
    else:
      flash('Venue ' + request.form['name'] + ' was NOT successfully listed!')
    return render_template('pages/home.html')
    # TODO: on unsuccessful db insert, flash an error instead.
    # DONE
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # DONE
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # DONE
  search_term=request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
  data = []
  for artist in artists:
    artist_d = artist.__dict__
    data.append({
      "id": artist_d['id'],
      "name": artist_d['name'],
      "num_upcoming_shows": Show.query.filter(Show.id == artist_d['id']).count()
    })
  response={
    "count": len(artists),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  # DONE
  artist = Artist.query.get(artist_id)
  artist_dict = artist.__dict__
  today = datetime.today()

  upcoming_shows = Show.query.filter(Show.start_time >= today, Show.artist_id == artist_id).all()
  upcoming_shows_dict = artist_show_list_to_dict(upcoming_shows)
  artist_dict['upcoming_shows'] = upcoming_shows_dict
  artist_dict['upcoming_shows_count'] = len(upcoming_shows_dict)

  past_shows = Show.query.filter(Show.start_time < today, Show.artist_id == artist_id).all()
  past_shows_dict = artist_show_list_to_dict(past_shows)
  artist_dict['past_shows'] = past_shows_dict
  artist_dict['past_shows_count'] = len(past_shows_dict)

  return render_template('pages/show_artist.html', artist=artist_dict)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter(Artist.id == artist_id).first()
  form.name.data=artist.name
  form.city.data=artist.city
  form.state.data=artist.state
  form.phone.data=artist.phone
  form.image_link.data=artist.image_link
  form.genres.data=artist.genres
  form.facebook_link.data=artist.facebook_link
  form.website.data=artist.website
  form.image_link.data=artist.image_link
  if str(artist.seeking_venue) == 'True':
    form.seeking_venue.data='Yes'
  else:
    form.seeking_venue.data='No'
  form.seeking_description.data=artist.seeking_description

  # TODO: populate form with fields from artist with ID <artist_id>
  # DONE
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  # DONE
  error = False
  body = {}
  try:
    genres_list = request.form.getlist('genres')
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = genres_list
    artist.facebook_link = request.form['facebook_link']
    artist.website = request.form['website']
    artist.image_link = request.form['image_link']
    if request.form['seeking_venue'] == 'Yes':
      artist.seeking_venue = True
    else:
      artist.seeking_venue = False
    artist.seeking_description = request.form['seeking_description']
    db.session.commit()
    body['name'] = artist.name
  except:
    error = True
    db.session.rollback()
    print( sys.exc_info() )
  finally:
    db.session.close()
    if not error:
      flash('Artist ' + body['name'] + ' was successfully updated!')
      return redirect(url_for('show_artist', artist_id=artist_id))
    else:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
      return redirect(url_for('server_error'))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter(Venue.id == venue_id).first()
  form.name.data=venue.name
  form.city.data=venue.city
  form.state.data=venue.state
  form.address.data=venue.address
  form.phone.data=venue.phone
  form.image_link.data=venue.image_link
  form.genres.data=venue.genres
  form.facebook_link.data=venue.facebook_link
  form.website.data=venue.website
  form.image_link.data=venue.image_link
  if str(venue.seeking_talent) == 'True':
    form.seeking_talent.data='Yes'
  else:
    form.seeking_talent.data='No'
  form.seeking_description.data=venue.seeking_description
  # TODO: populate form with values from venue with ID <venue_id>
  # DONE
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  body = {}
  try:
    genres_list = request.form.getlist('genres')
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.genres = genres_list
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website']
    venue.image_link = request.form['image_link']
    if request.form['seeking_talent'] == 'Yes':
      venue.seeking_talent = True
    else:
      venue.seeking_talent = False
    venue.seeking_description = request.form['seeking_description']
    db.session.commit()
    body['name'] = venue.name
  except:
    error = True
    db.session.rollback()
    print( sys.exc_info() )
  finally:
    db.session.close()
    if not error:
      flash('Venue ' + body['name'] + ' was successfully updated!')
      return redirect(url_for('show_venue', venue_id=venue_id))
    else:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
      return redirect(url_for('server_error'))

  #return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # DONE
  error = False
  bool_seeking_venue = True
  body = {}
  try:
    form = request.form
    genres_list = request.form.getlist('genres')
    if form['seeking_venue'] == 'Yes':
      bool_seeking_venue = True
    else:
      bool_seeking_venue = False
    artist = Artist(
      name= form['name'],
      genres = genres_list,
      city = form['city'],
      state = form['state'],
      phone = form['phone'],
      facebook_link = form['facebook_link'],
      website = form['website'],
      image_link = form['image_link'],
      seeking_venue = bool_seeking_venue,
      seeking_description = form['seeking_description']
    )
    db.session.add(artist)
    db.session.commit()
    body['name'] = artist.name
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if not error:
      # on successful db insert, flash success
      flash('Artist ' + body['name'] + ' was successfully listed!')
    else:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    return render_template('pages/home.html')
    # TODO: on unsuccessful db insert, flash an error instead.
    # DONE
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # DONE
  shows = Show.query.all()
  data = []
  for show in shows:
    show_d = show.__dict__
    show_d['start_time'] = str(show_d['start_time'])
    show_d['venue_name'] = show.venue.name
    show_d['artist_image_link'] = show.artist.image_link
    show_d['artist_name'] = show.artist.name
    data.append(show_d)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # DONE
  error = False
  try:
    form = request.form
    show = Show(
      artist_id = form['artist_id'],
      venue_id = form['venue_id'],
      start_time = form['start_time']
    )
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if not error:
      # on successful db insert, flash success
      flash('Show was successfully listed!')
    else:
      flash('An error occurred. Show could not be listed.')
    return render_template('pages/home.html')
    # TODO: on unsuccessful db insert, flash an error instead.
    # DONE
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

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
