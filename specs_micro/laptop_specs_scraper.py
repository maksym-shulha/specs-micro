import json
import logging

import httpx
from bs4 import BeautifulSoup

from configs.db_config import save_to_mongodb, find_by_url


logging.basicConfig(level=logging.ERROR,
                    filename='log_files/specs_scraper.log',
                    filemode='a',
                    format='{asctime} - {name} - {levelname} - {message}',
                    style='{'
                    )

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
           Chrome/102.0.5042.108 Safari/537.36'}


async def get_items_specs(filter_params: list) -> list:
    """
    Fetches specifications of laptops based on filter parameters and saves them to MongoDB.

    Args:
        filter_params (list): List of filter parameters.

    Returns:
        list: List of URLs for which specifications were fetched.
    """
    items_url_list = await get_items_urls(filter_params)
    producer = ''
    series = ''
    model = ''
    cpu = ''
    gpu = ''
    displaysize = ''

    async with httpx.AsyncClient() as client:
        for item_url in items_url_list:
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
                                displaysize = value

                            parameters[name] = value

                        items[category_name] = parameters

                    await save_to_mongodb({'producer': producer,
                                           'series': series,
                                           'cpu': cpu,
                                           'gpu': gpu,
                                           'displaysize': float(displaysize.strip('"')),
                                           'model': model,
                                           'price': price,
                                           'url': item_url,
                                           'specs': items})

            except httpx.RequestError as e:
                logging.error(f"Request failed for URL {item_url}: {e}")

    return items_url_list


async def get_items_urls(filter_params: list) -> list:
    """
    Retrieves a list of laptop page URLs based on filter parameters.

    Args:
        filter_params (list): List of filter parameters.

    Returns:
        list: List of item URLs.
    """
    brain_codes = []
    scrape = True

    try:
        with open('brain_codes.json', 'r') as f:
            mapping = json.load(f)
            for item in filter_params:
                brain_codes.append(mapping[item.lower()])

    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error reading 'brain_codes.json': {e}")
        return []

    query = ','.join(brain_codes)
    full_urls_list = []
    page_num = 1

    async with httpx.AsyncClient() as client:
        while scrape is True:
            full_search_url = 'https://brain.com.ua/ukr/category/Noutbuky-c1191/filter=' + query + f';page={page_num}/'
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

                    if buy_link is not None:
                        urls_list.append(f'https://brain.com.ua{item_url}')
                    else:
                        scrape = False
                        break

            except httpx.RequestError as e:
                logging.error(f"Request failed: {e}")

            if urls_list:
                full_urls_list.extend(urls_list)
                page_num += 1

    return full_urls_list
