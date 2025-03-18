import psycopg2
import psycopg2.extras
from flask import current_app, g
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def get_db():
	"""
	Get SQLAlchemy connection for ORM operations
	"""
	if 'db' not in g:
		g.db = db.session
	return g.db

def get_db_connection():
	"""
	Get raw psycopg2 connection for direct SQL execution
	"""
	if 'db_conn' not in g:
		g.db_conn = psycopg2.connect(
			current_app.config['SQLALCHEMY_DATABASE_URI'],
			cursor_factory=psycopg2.extras.DictCursor
		)

	return g.db_conn

def close_db(e=None):
	"""
	Close SQLAlchemy session explicitly if needed
	"""
	db_session = g.pop('db', None)

	if db_session is not None:
		db_session.close()

	# Close direct psycopg2 connection if it exists
	db_conn = g.pop('db_conn', None)
	if db_conn is not None:
		db_conn.close()

def init_app(app):
	# Initialize SQLAlchemy with the app
	db.init_app(app)

	# Register close_db function to be called when the application context ends
	app.teardown_appcontext(close_db) 


