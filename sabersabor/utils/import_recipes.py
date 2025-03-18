import json
import os 
from flask import current_app
from sabersabor.models import db, Recipe, Ingredient

def import_recipes(directory:str ='data/recipes_json'):
	"""
	Import recipes from .json files into the database

	Args:
		directory (str): Path to directory with .json files relative to app root
	"""

	# Handle both absolute and relative paths
	if os.path.isabs(directory):
		json_dir = directory
	else:
		root_dir = os.path.dirname(current_app.instance_path)
		json_dir = os.path.join(root_dir, directory)

	#Track count statistics 
	imported_count = 0
	error_count = 0

	try:
		# Iterate through JSON files
		for filename in os.listdir(json_dir):
			if not filename.endswith('.json'):
				continue

			if 'fixed' not in filename:
				continue
			
			file_path = os.path.join(json_dir, filename)

			# Load JSON recipe data
			try:
				with open(file_path, 'r') as f:
					data = json.load(f)
				
				# Make sure JSON file contains list of recipes
				recipes_to_process = []
				if isinstance(data, list):
					recipes_to_process = data
				else:
					recipes_to_process = [data]

				# Loop through all recipes in .JSON
				for recipe_data in recipes_to_process:
					# Check if recipe exists in database
					existing_recipe = Recipe.query.filter_by(url=recipe_data.get('url', '')).first()
					if existing_recipe:
						print(f'Recipe already exists: {recipe_data.get('title', 'Unknown')}')
						continue
					# Create Recipe object 
					recipe = Recipe(
						author=recipe_data.get('author', ''),
						title=recipe_data.get('title', ''),
						cook_time_minutes=recipe_data.get('cook_time_minutes', 0),
						prep_time_minutes=recipe_data.get('prep_time_minutes', 0),
						total_time_minutes=recipe_data.get('total_time_minutes', 0),
						description=recipe_data.get('description', ''),
						footnotes=recipe_data.get('footnotes', ''),
						ingredients=json.dumps(recipe_data.get('ingredients', [])),
						instructions=recipe_data.get('instructions', ''),
						rating_stars=recipe_data.get('rating_stars', 0),
						review_count=recipe_data.get('review_count', 0),
						url=recipe_data.get('url', ''),
						photo_url=recipe_data.get('photo_url', '')
					)

					# Process ingredient list
					ingredient_list = recipe_data.get('ingredients', [])
					if isinstance(ingredient_list, list):

						for ingredient_name in ingredient_list:

							# Search for existing ingredient, create new otherwise
							ingredient = Ingredient.query.filter_by(name=ingredient_name).first()

							if not ingredient:
								ingredient = Ingredient(name=ingredient_name)
								db.session.add(ingredient)

							# Add ingredient to recipe ingredient list
							recipe.ingredient_list.append(ingredient)

					# Save recipe 
					db.session.add(recipe)
					db.session.commit()
					imported_count += 1

			except Exception as e:
				print(f'Error importing {filename}: {str(e)}')
				db.session.rollback()
				error_count += 1

		return {
			'imported': imported_count,
			'errors': error_count
		}

	except Exception as e:
		print(f'Error processing import: {str(e)}')
		return {
			'imported': imported_count,
			'errors': error_count,
			'error_message': str(e)
		}






