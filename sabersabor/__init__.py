import os

from flask import Flask 
from flask_sqlalchemy import SQLAlchemy

def create_app(test_config=None):
	# create & configure sabersabor app 
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(
		SECRET_KEY='dev',
		SQLALCHEMY_DATABASE_URI='postgresql://brian:Geocache4571@localhost/sabersabor',
		SQLALCHEMY_TRACK_MODIFICATIONS=False
	)

	if test_config is None:
		# load the instance config when not testing, if it exists
		app.config.from_pyfile('config.py', silent=True)
	else:
		# load the test config if it was passed in
		app.config.from_mapping(test_config)

	# ensure instance folder exists
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	# simple page
	@app.route('/hello')
	def hello():
		return 'Hello World'

	from . import db 
	db.init_app(app)

	return app
