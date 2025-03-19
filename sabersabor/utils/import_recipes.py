import json
import os
from flask import current_app
from sabersabor.db import db
from sabersabor.models import Recipe, Ingredient

def import_recipes(directory:str ='data/recipes_json', batch_size=100):
    """
    Import recipes from .json files into the database with batch processing
    
    Args:
        directory (str): Path to directory with .json files relative to app root
        batch_size (int): Number of recipes to process in a single transaction
    """
    # Handle both absolute and relative paths
    if os.path.isabs(directory):
        json_dir = directory
    else:
        root_dir = os.path.dirname(current_app.instance_path)
        json_dir = os.path.join(root_dir, directory)
    
    # Track count statistics
    imported_count = 0
    error_count = 0
    
    # Track existing ingredients to avoid repeated queries
    ingredient_cache = {}
    
    try:
        # Iterate through JSON files
        for filename in os.listdir(json_dir):
            if not filename.endswith('.json'):
                continue
                
            if 'allrecipes-recipes-fixed_filtered' not in filename:
                continue
                
            file_path = os.path.join(json_dir, filename)
            
            print(f"Processing file: {filename}")
            
            # Load JSON recipe data
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Make sure JSON file contains list of recipes
                recipes_to_process = []
                if isinstance(data, list):
                    recipes_to_process = data
                else:
                    recipes_to_process = [data]
                
                print(f"Found {len(recipes_to_process)} recipes in {filename}")
                
                # Process in batches to reduce memory usage and improve performance
                batch_counter = 0
                
                # Loop through all recipes in JSON
                for idx, recipe_data in enumerate(recipes_to_process):
                    print(f"DEBUG: Processing recipe {idx+1}")
                    print(f"DEBUG: Type of recipe_data: {type(recipe_data)}")
                    
                    try:
                        # Make sure recipe_data is a dictionary
                        if not isinstance(recipe_data, dict):
                            print(f"Skipping non-dictionary recipe data: {recipe_data}")
                            continue
                            
                        # Check if recipe exists in database
                        url = recipe_data.get('url', '')
                        if not url:  # Skip recipes without URL
                            continue
                            
                        existing_recipe = Recipe.query.filter_by(url=url).first()
                        if existing_recipe:
                            print(f'Recipe already exists: {recipe_data.get("title", "Unknown")}')
                            continue
                            
                        # Get recipe title for error reporting
                        recipe_title = recipe_data.get('title', 'Unknown')
                        print(f"DEBUG: Processing recipe: {recipe_title}")
                            
                        # Create Recipe object with safe defaults
                        try:
                            recipe = Recipe(
                                author=recipe_data.get('author', ''),
                                title=recipe_title,
                                cook_time_minutes=int(recipe_data.get('cook_time_minutes', 0) or 0),
                                prep_time_minutes=int(recipe_data.get('prep_time_minutes', 0) or 0),
                                total_time_minutes=int(recipe_data.get('total_time_minutes', 0) or 0),
                                description=recipe_data.get('description', ''),
                                footnotes=recipe_data.get('footnotes', ''),
                                ingredients=json.dumps(recipe_data.get('ingredients', [])),
                                instructions=recipe_data.get('instructions', ''),
                                rating_stars=float(recipe_data.get('rating_stars', 0) or 0),
                                review_count=int(recipe_data.get('review_count', 0) or 0),
                                url=url,
                                photo_url=recipe_data.get('photo_url', '')
                            )
                            print(f"DEBUG: Recipe object created successfully")
                        except Exception as e:
                            print(f"Error creating Recipe object for '{recipe_title}': {str(e)}")
                            error_count += 1
                            continue
                        
                        # Add recipe to session first to get an ID
                        db.session.add(recipe)
                        db.session.flush()
                        print(f"DEBUG: Recipe added to session with ID: {recipe.id}")
                        
                        # Process ingredient list - track which ingredients we've already added
                        added_ingredient_ids = set()
                        ingredient_list = recipe_data.get('ingredients', [])
                        print(f"DEBUG: Processing {len(ingredient_list) if isinstance(ingredient_list, list) else 'unknown'} ingredients")
                        
                        if isinstance(ingredient_list, list):
                            for i, ingredient_name in enumerate(ingredient_list):
                                print(f"DEBUG: Processing ingredient #{i+1}: {ingredient_name}")
                                # Skip empty ingredients
                                if not ingredient_name or not isinstance(ingredient_name, str):
                                    print(f"DEBUG: Skipping invalid ingredient: {ingredient_name}")
                                    continue
                                    
                                # Check ingredient_cache before database query
                                if ingredient_name in ingredient_cache:
                                    print(f"DEBUG: Found ingredient '{ingredient_name}' in cache")
                                    ingredient = ingredient_cache[ingredient_name]
                                else:
                                    print(f"DEBUG: Looking up ingredient '{ingredient_name}' in database")
                                    # Use no_autoflush to prevent warning
                                    with db.session.no_autoflush:
                                        # Search for existing ingredient, create new otherwise
                                        ingredient = Ingredient.query.filter_by(name=ingredient_name).first()
                                    
                                    if not ingredient:
                                        print(f"DEBUG: Creating new ingredient '{ingredient_name}'")
                                        ingredient = Ingredient(name=ingredient_name)
                                        db.session.add(ingredient)
                                        # Flush to get the ID without committing
                                        db.session.flush()
                                        print(f"DEBUG: New ingredient created with ID: {ingredient.id}")
                                    else:
                                        print(f"DEBUG: Found existing ingredient with ID: {ingredient.id}")
                                    
                                    ingredient_cache[ingredient_name] = ingredient
                                
                                # Only add the ingredient if we haven't added it already for this recipe
                                if ingredient.id not in added_ingredient_ids:
                                    print(f"DEBUG: Adding ingredient {ingredient.id} to recipe {recipe.id}")
                                    recipe.ingredient_list.append(ingredient)
                                    added_ingredient_ids.add(ingredient.id)
                                else:
                                    print(f"DEBUG: Skipping duplicate ingredient {ingredient.id}")
                        
                        batch_counter += 1
                        print(f"DEBUG: Recipe {recipe_title} processed successfully")
                        
                        # Commit every batch_size recipes
                        if batch_counter >= batch_size:
                            print(f"Committing batch of {batch_size} recipes...")
                            db.session.commit()
                            imported_count += batch_counter
                            batch_counter = 0
                            # Clear SQLAlchemy session to avoid memory issues
                            db.session.expunge_all()
                            # Also clear the ingredient cache to prevent memory buildup
                            ingredient_cache = {}
                            
                    except Exception as e:
                        # Be very careful here - check the type before calling .get()
                        if isinstance(recipe_data, dict):
                            title = recipe_data.get("title", "Unknown")
                        else:
                            title = "Unknown (non-dictionary recipe data)"
                            print(f"DEBUG: Error - recipe_data is type {type(recipe_data)}, not a dictionary")
                            
                        print(f'Error importing recipe "{title}": {str(e)}')
                        # Rollback the current transaction
                        db.session.rollback()
                        error_count += 1
                        # Continue with next recipe instead of failing the whole batch
                        continue
                
                # Commit any remaining recipes in the final batch
                if batch_counter > 0:
                    print(f"Committing final batch of {batch_counter} recipes...")
                    db.session.commit()
                    imported_count += batch_counter
                
            except Exception as e:
                print(f'Error processing file {filename}: {str(e)}')
                db.session.rollback()
                error_count += 1
        
        # Final statistics
        print(f"Import completed. Total imported: {imported_count}, Total errors: {error_count}")
        return {
            'imported': imported_count,
            'errors': error_count
        }
        
    except Exception as e:
        print(f'Fatal error during import: {str(e)}')
        return {
            'imported': imported_count,
            'errors': error_count,
            'error_message': str(e)
        }