import requests
from bs4 import BeautifulSoup as bs
import json
from base64 import b64decode
import os
import pandas as pd
from urllib.parse import urljoin



DOMAIN = "https://www.flipkart.com"
LINKS_FOLDER = "flipkart_links_folder"
LINKS_SELECTOR = "a.CGtC98"
LINKS_FILE_PREFIX = "flipkark_links"
DATA_FOLDER = "flipkart_data_folder"
DATA_FILE_PREFIX = "flipkart_data"
PAGE_NUM = 1

def create_dirs():
    if not [each for each in os.walk('.') if f'{LINKS_FOLDER}' in each[0]]:
        os.system(f"mkdir {LINKS_FOLDER}")
    elif not [each for each in os.walk('.') if f'{DATA_FOLDER}' in each[0]]:
        os.system(f"mkdir {DATA_FOLDER}")


def get_page_using_proxy(url):
    api_response = requests.post(
        "https://api.zyte.com/v1/extract",
        auth=("<API KEY>", ""),
        json={
            "url": url,
            "httpResponseBody": True,
        },
    )
    if api_response.status_code == 200:
        http_response_body: bytes = b64decode(
            api_response.json()["httpResponseBody"])
        return http_response_body
    else: 
        return ""

def write_links(links, page_num):
    name = f"./{LINKS_FOLDER}/{LINKS_FILE_PREFIX}-{page_num}.csv"
    df = pd.DataFrame(links)
    df.to_csv(name, index=False)
    
import re
def page_details(soup):
    ele = soup.find("span", "BUOuZu")
    if ele:
        list_ = re.findall(r'\d+,\d+|\d+',ele.text)
        details = {}
        details["link_start"] = int(list_[0].replace(",",""))
        details["link_end"] = int(list_[1].replace(",",""))
        details["links_total"] = int(list_[2].replace(",",""))
        return details
    else:
        return {}





CSV_HEADERS = ("link", "link_position")
def get_links(url):
    global PAGE_NUM
    url = url.replace("&page=1", f"&page={str(PAGE_NUM)}")
    print(" Getting page links:", url+"...")
    res = get_page_using_proxy(url)
    # import ipdb; ipdb.set_trace()
    if res:
        soup = bs(res, 'html.parser')
        pg_details = page_details(soup)
        tag, class_ = LINKS_SELECTOR.split(".")
        links = [dict(zip(CSV_HEADERS,(each.get("href"), link_num))) for link_num, each in enumerate(soup.find_all(tag, class_),start=1)]
        if links:
            print(links)
            write_links(links, str(PAGE_NUM))
            if PAGE_NUM < pg_details.get("links_total"):
                if TEST and PAGE_NUM >= 5:
                    PAGE_NUM = 1
                    return
                PAGE_NUM += 1
                get_links(url)


def get_text(data):
    list_ = []
    for each in data:  
        if each:
             if each.name == 'img':
                list_.append(each.get("src"))
                continue
             text = re.sub(r"\xa0{1,}|\n{1,}", " ", each.text)
             
             list_.append(text)
        else:
            list_.append("")
    return list_

CSV_DATA_HEADERS = ["name", "price", "image_url", "description", "rating", "rating_"]

def clean_data(data):
    if data.get("rating_"):
        list_ = re.findall(r'(\d+,\d+)', data.get("rating_"))
        if list_:
            data["rating_count"] = list_[0].replace(",","")
            data["review_count"] = list_[-1].replace(",","")
            del data["rating_"]

def extract_data_frm_pg(soup):
    all_details_ele = soup.find("div","DOjaWF gdgoEp col-8-12")
    if all_details_ele:
        name = all_details_ele.find("h1")
        price = all_details_ele.find("div","Nx9bqj CxhGGd")
        image_url = soup.find("img","DByuf4 IZexXJ jLEJ7H")
        description = soup.find("div", "yN+eNk w9jEaj")
        rating = soup.find("div", "XQDdHH")
        rating_=soup.find("span", "Wphh3N")
        list_ = get_text([name, price, image_url, description, rating, rating_])
        data = dict(zip(CSV_DATA_HEADERS, list_))
        clean_data(data)
        return data


def get_data(page_num):
    all_ = []
    name = f"./{LINKS_FOLDER}/{LINKS_FILE_PREFIX}-{page_num}.csv"
    df = pd.read_csv(name)
    # import ipdb; ipdb.set_trace()
    for index, link_details in df.iterrows():
        link = link_details.get("link")
        print("Extracting link", link[:20]+"...")
        url = urljoin(DOMAIN, link)
        res = get_page_using_proxy(url)
        if res:
            soup = bs(res, 'html.parser')
            data = extract_data_frm_pg(soup)
            # print(data)
            data.update({"url":url})
            all_.append(data)
            if index > 4:
                break
    write_data(all_, page_num)
    

def write_data(data, page_num):
    name = f"./{DATA_FOLDER}/{DATA_FILE_PREFIX}-{page_num}.csv"
    df = pd.DataFrame(data)
    df.to_csv(name, index=False)

def loop_pages():
    csv_files = [files for dir_name, n, files in os.walk(f"./{LINKS_FOLDER}")][0]
    for filename in csv_files:
        pg_num = int(re.findall('\d+', filename)[0])
        get_data(pg_num)



if __name__ == '__main__':
    TEST = True
    create_dirs()
    url = "https://www.flipkart.com/search?q=mobiles&marketplace=FLIPKART&page=1"
    get_links(url)
    loop_pages()







