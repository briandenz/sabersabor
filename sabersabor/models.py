from datetime import date 
from sabersabor.db import db

#Recipe-Ingredient many-to-many association table
recipe_ingredients = db.Table(
	'recipe_ingredients',
	db.Column('recipe_id', db.Integer, db.ForeignKey('recipes.id'), primary_key=True), 
	db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredients.id'), primary_key=True)
)

class Recipe(db.Model):
	__tablename__ = 'recipes'

	id = db.Column(db.Integer, primary_key=True)
	author = db.Column(db.String(50), nullable=False)
	title = db.Column(db.String(150), nullable=False)
	cook_time_minutes = db.Column(db.Integer, nullable=False)
	prep_time_minutes = db.Column(db.Integer, nullable=False)
	total_time_minutes = db.Column(db.Integer, nullable=False)
	description = db.Column(db.Text)
	error = db.Column(db.Boolean, nullable=False, default=False)
	footnotes = db.Column(db.Text)
	ingredients = db.Column(db.Text)
	instructions = db.Column(db.Text)
	rating_stars = db.Column(db.Numeric(3, 2), nullable=False)
	review_count = db.Column(db.Integer, nullable=False)
	time_scraped = db.Column(db.Date, default = date.today)
	url = db.Column(db.String(255), nullable=False)
	photo_url = db.Column(db.String(255), nullable=False)

	ingredient_list = db.relationship('Ingredient', secondary='recipe_ingredients', backref='recipes')

class Ingredient(db.Model):
	__tablename__ = 'ingredients'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), unique=True, nullable=False)
	


