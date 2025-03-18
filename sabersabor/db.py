import psycopg2
import psycopg2.extras

import click
from flask import current_app, g
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db():
	# Get raw connection to execute SQL
	conn = get_db_connection()
	conn.autocommit = True

	with conn.cursor() as cursor:
		with current_app.open_resource('schema.sql') as f:
			cursor.execute(f.read().decode('utf-8'))

	# Conn is not closed here because it's managed by Flask app context

@click.command('init-db')
def init_db_command():
	"""
	Clear existing data and create new tables
	"""
	with current_app.app_context(): # Ensure existence of app context
		init_db()
		click.echo('Initialized database')


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
	# Register close_db function to be called when the application context ends
	app.teardown_appcontext(close_db)
	app.cli.add_command(init_db_command)


