import os
import django
import requests
import json
from bs4 import BeautifulSoup


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "specs_micro.settings")
django.setup()

from template_specs.models import Producer, Series, Cpu, Gpu, Category, DisplaySize

headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome\
        /102.0.5042.108 Safari/537.36'}

param_mapping = {
    'Producer': Producer,
    'Series': Series,
    'Cpu': Cpu,
    'Gpu': Gpu,
    'Category': Category,
    'DisplaySize': DisplaySize,
}


def get_items_specs(**kwargs):
    full_search_url = make_search_url(**kwargs)
    items_url_list = get_items_urls(full_search_url)

    with open('specs_list.json', 'w') as f:
        model = ''
        specs = {}

        for item_url in items_url_list:
            response = requests.get(item_url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
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

                    parameters[name] = value

                items[category_name] = parameters

            specs[model] = items
        f.write(json.dumps(specs, ensure_ascii=False, indent=2))


def make_search_url(**kwargs):
    base_url = 'https://brain.com.ua/ukr/category/Noutbuky-c1191/filter='
    search_params_lst = []

    for key, value in kwargs.items():
        filter_code = param_mapping[key].objects.get(name=value).code
        search_params_lst.append(filter_code)

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


get_items_specs(Producer='HP', Series='HP Zbook')
