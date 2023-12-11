import os
import django
import requests
from bs4 import BeautifulSoup

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "specs_micro.settings")
django.setup()

from template_specs.models import Producer, Series, Cpu, Gpu, Category, DisplaySize

url = "https://brain.com.ua/ukr/category/Noutbuky-c1191/"

headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5042.108 Safari/537.36"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

filter_wrapper_div = soup.find("div", {"class": "filters-wrapper"})

param_mapping = {
    "Виробник": Producer,
    "Серія (модельний ряд)": Series,
    "Процесор": Cpu,
    "Серія дискретної відеокарти": Gpu,
    "Тип ноутбуку": Category,
    "Діагональ дисплея": DisplaySize,
}

for param in filter_wrapper_div.find_all("div", {"class": "filter__item"}):
    try:
        param_name = param.find("div", {"class": "filter__title"}).text.strip()

        if param_name in param_mapping:

            for a in param.find_all('a', {"class": "link_checkbox"}):
                item_name = a.text.strip()
                item_code = a['data-filter']
                model_class = param_mapping[param_name]
                model_class.objects.create(name=item_name, code=item_code)

    except Exception as e:
        pass
