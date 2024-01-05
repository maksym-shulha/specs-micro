import logging
import requests
from bs4 import BeautifulSoup

from configs.db_config import collection


logging.basicConfig(level=logging.ERROR,
                    filename='log_files/specs_scraper.log',
                    filemode='a',
                    format='{asctime} - {name} - {levelname} - {message}',
                    style='{'
                    )


headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
           Chrome/102.0.5042.108 Safari/537.36'}


def update_prices():
    """
    Updates prices for laptops in the MongoDB collection by scraping the latest price from their respective URLs.
    If a price is successfully scraped, it updates the database entry; otherwise, it deletes the entry.
    """
    laptops = collection.find()

    for laptop in laptops:
        url = laptop['url']
        updated_price = scrape_price_from_url(url)

        if updated_price is None:
            collection.delete_one({'_id': laptop['_id']})
        elif updated_price != laptop['price']:
            collection.update_one({'_id': laptop['_id']}, {'$set': {'price': updated_price}})
            print(f"Updated price for {laptop['model']} to {updated_price}")


def scrape_price_from_url(url: str):
    """
    Scrapes the price of a laptop from the specified URL.

    Returns:
        int or None: The scraped price as an integer if successful, or None if an error occurs during scraping.
    """
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        updated_price = int(soup.find('span', {'itemprop': 'price'})['content'])
        return updated_price

    except Exception as e:
        logging.error(f"Error scraping price for {url}: {e}")
        return None


if __name__ == "__main__":
    update_prices()
