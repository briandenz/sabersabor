import utility_functions

def main():
	url = "https://www.allrecipes.com/recipes-a-z-6735880"
	links = utility_functions.get_all_links(url) 

if __name__ == "__main__":
	main()