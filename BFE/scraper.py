import requests
from bs4 import BeautifulSoup

def scrape_dog_food():
    url = "https://hexomatic.com/academy/2023/10/16/top-30-most-scraped-websites-in-2023/#1-amazon-best-site-for-scraping-ecommerce-data"  # Replace with a real URL
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}


    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return ["Error: Unable to fetch data"]

    soup = BeautifulSoup(response.text, 'html.parser')

    deals = []
    for item in soup.select('.product'):  # Adjust based on website structure
        title = item.select_one('.title').text
        price = item.select_one('.price').text
        deals.append(f"{title} - {price}")

    return deals
#trail to find problem in code
def scrape_dog_food():
    url = "http://books.toscrape.com/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return ["Error: Unable to fetch data"]

    soup = BeautifulSoup(response.text, 'html.parser')

    deals = []
    for item in soup.select('.product_pod'):
        title = item.select_one('h3 a').text
        price = item.select_one('.price_color').text
        deals.append(f"{title} - {price}")

    return deals
