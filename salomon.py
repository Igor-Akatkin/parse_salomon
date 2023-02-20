import os.path
import json
import requests
import time

from bs4 import BeautifulSoup


base_url = "https://salomon.kz"
# url = f"{base_url}/woman/obuv-1"
url = f"{base_url}/man/obuv-2"

# print(f"[INFO] Начинаем парсинг по категории {url}")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
}

def get_big_page(url):
    """Получаем страницу со всеми товарами категории"""
    # s = requests.Session()
    # response = s.get(url=url, headers=headers).text
    response = requests.get(url, headers=headers).text
    # big_page = f"https://salomon.kz/man/obuv-2?start=0&limit=9999999"
    big_page = f"{url}?start=0&limit=9999999"
    return big_page

def get_urls(big_page):
    """Получаем ссылки на товары"""
    req = requests.get(url=big_page, headers=headers).text
    soup = BeautifulSoup(req, "lxml")
    item_urls = soup.find_all("div", class_="block_product")

    # сохраняем ссылки на товары в объекте списка
    item_urls_list = []
    for i in item_urls:
        url = i.find("a", class_="btn button_detail")
        url = base_url + url.get("href")
        item_urls_list.append(url)

    return item_urls_list

def get_data(item_urls_list):
    """Парсинг данных"""
    print("[INFO] Начинаем парсинг данных")

    urls_count = len(item_urls_list)
    print(f"[INFO] Всего товаров: {urls_count}")
    count = 1

    result_list = []
    for url in item_urls_list:
        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")

        # Категория товара:
        try:
            item_category = soup.find("div", class_="white-block").find("h1").text.split(" ")[0]
        except Exception as ex:
            item_category = None

        # Название товара:
        try:
            item_name = soup.find("div", class_="white-block").find("h1").text.partition(' ')[2]
        except Exception as ex:
            item_name = None

        # Размеры:
        item_size_list = []
        try:
            item_sizes = soup.find_all("span", class_="input_type_radio")
            for size in item_sizes:
                item_size = size.text.strip()
                item_size_list.append(item_size)
        except Exception as ex:
            item_size_list = None

        # Артикул:
        try:
            item_article = soup.find("span", {"id": "product_code"}).text.strip()
        except Exception as ex:
            item_article = None

        # Цвет товара:
        try:
            item_color = soup.find("div", class_="white-block").find("div", class_="extra_field").text.split()[1].strip()
        except Exception as ex:
            print(ex)
            item_color = None

        # Состав:
        try:
            item_composition = soup.find("div", class_="white-block").find("div", class_="extra_field").find_next().text.partition(' ')[2].strip()
        except Exception as ex:
            print(ex)
            item_composition = None

        # Цена:
        try:
            item_price = soup.find("span", {"id": "block_price"}).text.split()[0].strip()
        except Exception as ex:
            print(ex)
            item_price = None


        result_list.append(
            {
                "Категория": item_category,
                "Название": item_name,
                "Ссылка": url,
                "Размеры": item_size_list,
                "Цена": item_price,
                "Цвет": item_color,
                "Состав": item_composition,
                "Артикул": item_article
            }
        )

        print(f"[+] Processed: {count}/{urls_count}")
        count += 1

    result = json.dumps(result_list, ensure_ascii=False, indent=4)
    return result

def save_to_json(result):
    with open("result.json", "w") as file:
        print(result, file=file)

# def do_filter():
#     with open('result.json',encoding="utf-8") as file:
#         data = json.load(file)
#
#     datas = []
#     for i in data:
#         if i['Категория'] == 'Ботинки' and ("9" in ['Размеры'] or "9.5" in i['Размеры']):
#             datas.append(i)
#     json_data = json.dumps(datas, ensure_ascii=False)
#     print(json_data)

def main():
    start_time = time.time()
    big_page = get_big_page(url=url)
    item_urls_list = get_urls(big_page)
    result = get_data(item_urls_list)
    save_to_json(result)

    finish_time = time.time() - start_time
    print(f"Затраченное время на работу скрипта: {finish_time} секунд")
    # do_filter()

if __name__ == "__main__":
    main()