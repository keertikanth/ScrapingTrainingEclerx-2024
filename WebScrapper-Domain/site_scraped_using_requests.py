import requests
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
from copy import deepcopy
HEADERS = {
    "User-Agent" : "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Connection": "keep-alive",
    "Retry-After": "5"
}

HTTP_PROTOCOL= "https://"
DOMAIN = "webscraper.io"
MAIN_URL = "https://webscraper.io/test-sites/e-commerce/static/computers/tablets/"


def get_page(url):
    res = requests.get(url, headers=HEADERS, verify=False)
    if res.status_code == 200:
        return res
    

def parse_page(res):
    if res:
        soup = bs(res.text, 'html.parser')
        return soup
    

def extract_text(ele, type="str"):
    if ele:
        return cast_value(ele.text, type=type)
    else:
        return ""


def clean_text(text):
    if text:
        return re.sub("[\t\n]+", "", text)
    
def cast_value(text, type="str"):
    if text:
        text = clean_text(text)
        if type =="str":
            return text
        elif type =="int":
            return int(text)
    else:
        return ""

def check_presence(ele, list_=False, regex="", cast="str", ele_check=False):
    if ele_check:
        if ele:
            return ele

    if not list_ and  not regex:
        return extract_text(ele, type=cast)
    
    if list_ and ele:
        return ele
    elif list_:
        return []
    
    if ele and regex:
        match_ = re.match(regex, clean_text(ele.text))
        text = match_.group() if match_ else ""
        return cast_value(text, type=cast)
    elif regex:
        return ""

CSV_HEADERS = ("name", "price", "review")

def extract_elements(soup):
    if soup:
        all_cards = check_presence(soup.find_all("div", class_="card thumbnail"), list_=True)
        for card in all_cards:
            link = card.find("a","title").get("href", "")
            data = follow_link(HTTP_PROTOCOL+DOMAIN+link)
            yield data


def parse_selector(selector_str):
    tag_name = selector_str.split(".")[0]
    if '.'  in selector_str:
        class_=" ".join(selector_str.split(".")[1:])
    else:
        class_=""
    return tag_name, class_


def get_child_element(soup, path):
    soup = deepcopy(soup)
    for selector_str in path.split(" "):
        tag_name, class_ = parse_selector(selector_str)
        if soup:
            ele = soup.find(tag_name, class_)
            soup = ele if check_presence(ele, ele_check=True) else ""
        else:
            return       
    return soup
                    

def get_eles_inside_link(soup):
    name = check_presence(get_child_element(soup, "div.caption h4.title"))
    price = check_presence(soup.find("h4", "price")).strip("$")
    review = check_presence(get_child_element(soup, "div.ratings p.review-count"), regex=r"\d+", cast="int")
    return dict(zip(CSV_HEADERS,(name, price, review)))


def follow_link(link):
    if link:
        res = get_page(link) 
        soup = parse_page(res)
        card_data = get_eles_inside_link(soup)
        return card_data


def group_entity_data(soup):
    list_ = []
    for data in extract_elements(soup):
        list_.append(data)
    return list_

    
def create_csv(domain,data, num):
    if data:
        df = pd.DataFrame(data)
        df.to_csv(f"{domain}-page-{num}.csv", index=False)


def parse_url(url):
    if "?" in url:
        match_ = url.split("?")[-1].split("=")
        keys = [each for index, each in enumerate(match_,start=1) if index % 2 == 1 or index == 1]
        values = [each for index, each in enumerate(match_,start=1) if index % 2 == 0]
        query_params= dict(zip(keys, values))
        return query_params
    else:
        return {}


def execute_crawl_stack(url):
    res = get_page(url) 
    soup = parse_page(res)
    data = group_entity_data(soup)
    page_num = parse_url(url).get("page", 1)
    create_csv(DOMAIN, data, page_num)
    if data:
        follow_next_page(url)


def make_url(url, params):
    params_str = "?"
    for key, value in params.items():
        params_str= params_str+f"{key}={value}" 
    return url+params_str


def follow_next_page(url):
    params = parse_url(url)
    next_page = int(params.get("page", 1)) + 1
    params.update({"page":next_page})
    if next_page == 2:
        params.update({"page":"2"}) 
    url = make_url(MAIN_URL, params) 
    execute_crawl_stack(url)


if __name__ == '__main__':
    url = "https://webscraper.io/test-sites/e-commerce/static/computers/tablets/"
    execute_crawl_stack(url)
