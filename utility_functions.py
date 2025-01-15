from bs4 import BeautifulSoup
import requests

def get_all_links(url: str) -> list[str]:

	#sends GET to webpage
	response = requests.get(url)

	#parse html content of webpage
	soup = BeautifulSoup(response.text, 'html.parser')

	#find and extract text from all <a> tags
	links = [a['href'] for a in soup.find_all('a', href=True)]

	print(f"-----")
	print(f"Links on page {url}:")
	print(f"{links}")

	return(links)
