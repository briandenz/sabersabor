from recipe_urls import scrape_urls, scrape_html

def get_recipe_url(base_urls: list[str]) -> list[str]:
	compiled_recipe_links = []

	for base_url in base_urls:
		scraped_links = scrape_urls(base_url)
		print(f"-----")
		print(f"Scraped links for {base_url}:")
		print(f"-----")
		print(f"{scraped_links}")
		compiled_recipe_links.append(scraped_links)

	return compiled_recipe_links
