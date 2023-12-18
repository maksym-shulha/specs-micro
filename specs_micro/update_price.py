import requests
from bs4 import BeautifulSoup

from configs.db_config import collection


headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
           Chrome/102.0.5042.108 Safari/537.36'}


def update_prices():
    laptops = collection.find()

    for laptop in laptops:
        url = laptop['url']
        updated_price = scrape_price_from_url(url)

        if updated_price is not None:
            collection.update_one({'_id': laptop['_id']}, {'$set': {'price': updated_price}})
            print(f"Updated price for {laptop['model']} to {updated_price}")
        else:
            collection.delete_one({'_id': laptop['_id']})


def scrape_price_from_url(url):
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        updated_price = int(soup.find('span', {'itemprop': 'price'})['content'])
        return updated_price

    except Exception as e:
        print(f"Error scraping price for {url}: {e}")
        return None


if __name__ == "__main__":
    update_prices()
