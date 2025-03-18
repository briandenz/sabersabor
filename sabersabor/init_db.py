import os
import psycopg2

conn = psycopg2.connect(
	host='localhost',
	database='sabersabor',
	user=os.environ['DB_USERNAME'],
	password=os.environ['DB_PASSWORD'])

# Cursor to perform database operations
cur = conn.cursor()

# Create recipe table 
cur.execute('DROP TABLE IF EXISTS recipes;')
cur.execute('''
CREATE TABLE recipes (
    id serial PRIMARY KEY,
    author VARCHAR(50) NOT NULL,
    title VARCHAR(150) NOT NULL,
    cook_time_minutes INTEGER NOT NULL,
    prep_time_minutes INTEGER NOT NULL,
    total_time_minutes INTEGER NOT NULL,
    description TEXT,
    error BOOLEAN NOT NULL DEFAULT FALSE,
    footnotes TEXT,
    ingredients TEXT,
    instructions TEXT,
    rating_stars NUMERIC(3, 2) NOT NULL,
    review_count INTEGER NOT NULL,
    time_scraped DATE DEFAULT CURRENT_DATE,
    url VARCHAR(255) NOT NULL
);
''')