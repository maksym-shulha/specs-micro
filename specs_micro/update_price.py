import asyncio
import logging
import httpx
from bs4 import BeautifulSoup

from configs.db_config import collection

logging.basicConfig(level=logging.INFO,
                    filename='/specs_micro/log_files/update_price.log',
                    filemode='a',
                    format='{asctime} - {name} - {levelname} - {message}',
                    style='{'
                    )

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
           Chrome/102.0.5042.108 Safari/537.36'}


async def update_prices():
    """
    Asynchronously updates laptop prices in the database based on the latest scraped data.
    """

    laptops = collection.find()
    updated_prices = await scrape_prices()

    async for laptop in laptops:
        url = laptop['url']
        updated_price = updated_prices.get(url)

        if updated_price is None:
            await collection.delete_one({'_id': laptop['_id']})
        elif updated_price != laptop['price']:
            await collection.update_one({'_id': laptop['_id']}, {'$set': {'price': updated_price}})
            logging.info(f"Updated price for {laptop['model']} to {updated_price}")
    logging.info('Price updating completed')


async def scrape_prices():
    """
    Asynchronously scrapes laptop prices from a website and returns a dictionary with URLs and their
    corresponding prices.
    """
    scrape = True

    full_result = {}
    page_num = 1

    async with httpx.AsyncClient() as client:
        while scrape is True:
            full_search_url = f'https://brain.com.ua/ukr/category/Noutbuky-c1191/page={page_num}/'
            result = {}

            try:
                response = await client.get(full_search_url, headers=headers)

                if page_num == 1 and response.is_redirect:
                    return []
                elif page_num != 1 and response.is_redirect:
                    scrape = False
                    break

                soup = BeautifulSoup(response.content, 'html.parser')
                products_div = soup.find('div', {'id': 'view-grid'})

                for product in products_div.find_all('div', {'class': 'product-wrapper'}):
                    item_url = product.find('a', {'itemprop': 'url'})['href']
                    full_item_url = f'https://brain.com.ua{item_url}'
                    buy_link = product.find('a', {'class': 'add'})
                    price_tag = product.find('span', {'itemprop': 'price'})
                    price = int(price_tag.text) if price_tag else None

                    if buy_link:
                        result[full_item_url] = price
                    else:
                        scrape = False
                        break

            except httpx.RequestError as e:
                logging.error(f"Request failed: {e}")

            if result:
                full_result.update(result)
                page_num += 1

    return full_result


if __name__ == "__main__":
    asyncio.run(update_prices())
