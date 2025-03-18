-- Drop tables 
DROP TABLE IF EXISTS recipe_ingredients;
DROP TABLE IF EXISTS ingredients;
DROP TABLE IF EXISTS recipes;

-- Create ingredients table
CREATE TABLE ingredients (
	id SERIAL PRIMARY KEY,
	name VARCHAR(100) UNIQUE NOT NULL
);

-- Create recipe table
CREATE TABLE recipes (
	id SERIAL PRIMARY KEY,
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
	rating_stars NUMERIC(3,2) NOT NULL,
	review_count INTEGER NOT NULL,
	time_scraped DATE DEFAULT CURRENT_DATE,
	url VARCHAR(255) NOT NULL,
	photo_url VARCHAR(255) NOT NULL
	);

-- Create junction table
CREATE TABLE recipe_ingredients (
	recipe_id INTEGER REFERENCES recipes(id),
	ingredient_id INTEGER REFERENCES ingredients(id),
	PRIMARY KEY (recipe_id, ingredient_id)
);
