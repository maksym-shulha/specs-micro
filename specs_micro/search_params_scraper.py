import json
import logging
import requests

from bs4 import BeautifulSoup


logging.basicConfig(level=logging.ERROR,
                    filename='log_files/specs_scraper.log',
                    filemode='a',
                    format='{asctime} - {name} - {levelname} - {message}',
                    style='{'
                    )

url = 'https://brain.com.ua/ukr/category/Noutbuky-c1191/'

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
           Chrome/102.0.5042.108 Safari/537.36'}

param_mapping = {
    "Виробник": 'Producer',
    "Серія (модельний ряд)": 'Series',
    "Процесор": 'Cpu',
    "Серія дискретної відеокарти": 'Gpu',
    "Тип ноутбуку": 'Category',
    "Діагональ дисплея": 'DisplaySize',
}


def scrape_search_params():
    """
    Scrapes search parameters from a specified URL and saves the mapping to a JSON file.

    Raises:
        Exception: If there is an error while scraping and processing the search parameters.

    The function sends an HTTP request to the specified URL, extracts search parameters
    from the HTML content, and creates a mapping between item names and their corresponding codes.
    This mapping is then saved to a JSON file named 'brain_codes.json'.
    """
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    filter_wrapper_div = soup.find("div", {"class": "filters-wrapper"})
    brain_codes_mapping = {}

    for param in filter_wrapper_div.find_all("div", {"class": "filter__item"}):
        try:
            param_name = param.find("div", {"class": "filter__title"}).text.strip()

            if param_name in param_mapping:

                for a in param.find_all('a', {"class": "link_checkbox"}):
                    item_name = a.text.strip().lower()
                    item_code = a['data-filter']
                    brain_codes_mapping[item_name] = item_code

        except Exception as e:
            logging.error(f"Error while scraping search parameters: {e}")

    with open('brain_codes.json', 'w') as f:
        json.dump(brain_codes_mapping, f)


if __name__ == '__main__':
    scrape_search_params()
