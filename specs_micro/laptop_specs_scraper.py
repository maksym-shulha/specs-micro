import requests
from bs4 import BeautifulSoup

from configs.db_config import save_to_mongodb, find_by_url


headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
           Chrome/102.0.5042.108 Safari/537.36'}


def get_items_specs(query):
    items_url_list = get_items_urls(query)
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

    return items_url_list


def get_items_urls(query):
    full_urls_list = []
    scrape = True
    page_num = 1

    while scrape is True:
        full_search_url = 'https://brain.com.ua/ukr/category/Noutbuky-c1191/filter=' + query + f';page={page_num}/'
        urls_list = []

        try:
            response = requests.get(full_search_url, headers=headers, allow_redirects=False)

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

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

        if urls_list:
            full_urls_list.extend(urls_list)
            page_num += 1

    return full_urls_list
