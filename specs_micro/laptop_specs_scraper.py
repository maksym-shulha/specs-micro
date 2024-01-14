import asyncio
import json
import logging
import re

import httpx
from bs4 import BeautifulSoup

from configs.db_config import save_to_mongodb, find_by_url


logging.basicConfig(level=logging.INFO,
                    filename='/specs_micro/log_files/specs_scraper.log',
                    filemode='a',
                    format='{asctime} - {name} - {levelname} - {message}',
                    style='{'
                    )

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
           Chrome/102.0.5042.108 Safari/537.36'}


async def get_items_specs(filter_params=None):
    """
    Asynchronously scrapes laptop specifications from the Brain.com.ua website and saves them to the MongoDB database.

    Args:
        filter_params (list): A list of filter parameters to narrow down the laptop search.

    Returns:
        list: A list of URLs for the laptops processed during the scraping.
    """
    items_url_list = await get_items_urls(filter_params)

    async with httpx.AsyncClient() as client:
        for item_url in items_url_list:
            producer = ''
            series = ''
            model = ''
            cpu = ''
            gpu = ''
            displaysize = ''

            try:
                if not await find_by_url(item_url):
                    response = await client.get(item_url, headers=headers)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    price = int(soup.find('span', {'itemprop': 'price'})['content'])
                    all_specs = soup.find('div', {'class': 'br-pr-chr'})
                    items = {}

                    for category in all_specs.find_all('div', {'class': 'br-pr-chr-item'}):
                        category_name = category.find('p').text.strip()
                        parameters = {}

                        for div in category.find('div').find_all('div', recursive=False):
                            characteristics = div.find_all('span')
                            name = characteristics[0].text.strip()
                            value = characteristics[1].text.strip()

                            if name == 'Модель':
                                model = value
                            elif name == 'Серія (модельний ряд)':
                                series = value
                            elif name == 'Виробник':
                                producer = value
                            elif name == 'Процесор':
                                cpu = value
                            elif name == 'Відеокарта':
                                gpu = value
                            elif name == 'Діагональ дисплея':
                                displaysize = float(value.strip('"'))
                            elif name == "Об'єм SSD":
                                match = re.match(r'^(\d+)', value)
                                int_value = int(match.group(1))
                                if int_value < 10:
                                    volume = int_value * 1000
                                else:
                                    volume = int_value

                            parameters[name] = value

                        items[category_name] = parameters

                    await save_to_mongodb({'producer': producer,
                                           'series': series,
                                           'cpu': cpu,
                                           'gpu': gpu,
                                           'displaysize': displaysize,
                                           'model': model,
                                           'volume': volume,
                                           'price': price,
                                           'url': item_url,
                                           'specs': items})

                    logging.info(f"Laptop {series}, {model} was written to db")

            except httpx.RequestError as e:
                logging.error(f"Request failed for URL {item_url}: {e}")

    return items_url_list


async def get_items_urls(filter_params):
    """
    Asynchronously retrieves a list of laptop URLs based on the provided filter parameters.

    Args:
        filter_params (list): A list of filter parameters to narrow down the laptop search.

    Returns:
        list: A list of URLs for the laptops that match the filter parameters.
    """
    brain_codes = []
    scrape = True

    if filter_params:
        try:
            with open('/specs_micro/brain_codes.json', 'r') as f:
                mapping = json.load(f)
                for item in filter_params:
                    brain_codes.append(mapping[item.lower()])

        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Error reading 'brain_codes.json': {e}")
            return []

    query = ','.join(brain_codes)

    if filter_params:
        search_url = 'https://brain.com.ua/ukr/category/Noutbuky-c1191/filter=' + query + ';page='
    else:
        search_url = 'https://brain.com.ua/ukr/category/Noutbuky-c1191/page='

    full_urls_list = []
    page_num = 1

    async with httpx.AsyncClient() as client:
        while scrape is True:
            full_search_url = f'{search_url}{page_num}/'
            urls_list = []

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
                    buy_link = product.find('a', {'class': 'add'})

                    if buy_link:
                        urls_list.append(f'https://brain.com.ua{item_url}')
                    else:
                        scrape = False
                        break

            except httpx.RequestError as e:
                logging.error(f"Request failed: {e}")

            if urls_list:
                full_urls_list.extend(urls_list)
                page_num += 1

    logging.info(f"Urls list was created.")
    return full_urls_list


if __name__ == "__main__":
    asyncio.run(get_items_specs())
