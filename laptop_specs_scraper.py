import requests
from bs4 import BeautifulSoup

from specs_micro.configs.db_config import save_to_mongodb, find_by_url


headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome\
        /102.0.5042.108 Safari/537.36'}


def get_items_specs(*args):
    full_search_url = make_search_url(*args)
    items_url_list = get_items_urls(full_search_url)
    producer = ''
    series = ''
    model = ''

    for item_url in items_url_list:
        if not find_by_url(item_url):
            response = requests.get(item_url, headers=headers)
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

                    parameters[name] = value

                items[category_name] = parameters


            save_to_mongodb({'producer': producer,
                             'series': series,
                             'model': model,
                             'price': price,
                             'url': item_url,
                             'specs': items})


def make_search_url(*args):
    base_url = 'https://brain.com.ua/ukr/category/Noutbuky-c1191/filter='
    search_params_lst = [item for item in args]

    query_params = ','.join(search_params_lst)
    full_search_url = base_url + query_params + '/'

    return full_search_url


def get_items_urls(url):
    urls_list = []
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    products_div = soup.find('div', {'id': 'view-grid'})

    for product in products_div.find_all('div', {'class': 'product-wrapper'}):
        url = product.find('a', {'itemprop': 'url'})['href']
        buy_link = product.find('a', {'class': 'add'})

        if buy_link is not None:
            urls_list.append(f'https://brain.com.ua{url}')

    return urls_list


get_items_specs('9717-86045462600', '199-g36543')
