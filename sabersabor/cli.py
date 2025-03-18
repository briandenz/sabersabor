import click
from flask.cli import with_appcontext
from sabersabor.utils.import_recipes import import_recipes

@click.command('import-recipes')
@click.argument('directory', default='data/recipes_json')
@with_appcontext
def import_recipes_command(directory):
	"""
	Import recipes from JSON files in the specified directory
	"""
	click.echo(f'Importing recipes from {directory}')
	results = import_recipes(directory)
	click.echo(f'Import completed. Imported: {results['imported']}, Errors: {results['errors']}')
