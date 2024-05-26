import requests
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
from copy import deepcopy
import time
HEADERS = {
    "User-Agent" : "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Connection": "keep-alive",
    "Retry-After": "5"
}

HTTP_PROTOCOL= "https://"
DOMAIN = "amazon.com"
MAIN_URL = "https://www.amazon.com/s?k=laptops+and+accessories"
DEFAULT_SLEEP_TIME=1
FAIL_SLEEP_TIME = 5
TRIES=5
RESTRICT_LINKS = ["https://aax-us-iad.amazon.com","/sspa"]
CSV_DIRNAME ="amazon_scrape_folder"
CSV_HEADERS = ("name", "price", "avg_review_rating", "review_count")




def get_page_using_session(url):
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session.get(url, headers=HEADERS, verify=False)


def get_page(url):
    time.sleep(DEFAULT_SLEEP_TIME)
    count = 0
    while True:
        if count <= TRIES:
            count +=1
            # res = requests.get(url, headers=HEADERS, verify=False, timeout=10)
            res = get_page_using_session(url)
            if res.status_code == 200:
                return res
            else:
                time.sleep(FAIL_SLEEP_TIME)
        else:
            break
    return ""

    
def parse_page(res):
    if res:
        soup = bs(res.text, 'html.parser')
        return soup
    

def extract_text(ele, type="str"):
    if ele:
        return cast_value(clean_text(ele.text), type=type)
    else:
        return ""


def clean_text(text):
    if text:
        return re.sub("[\t\n]+", "", text).strip()


def cast_value(text, type="str"):
    if text:
        text = clean_text(text)
        if type =="str":
            return text
        elif type =="int":
            return int(text)
    else:
        return ""


def check_presence(ele, list_=False, regex="", cast="str", href=False):
    if href and ele:
        return ele.get("href", "")
    elif href:
        return ""
    
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


def get_detail_page_link(card):
    link_ele = card.find("div", "a-section a-spacing-small a-spacing-top-small puis-padding-right-small")
    if link_ele:
        link= check_presence(link_ele.find("a", "a-link-normal s-faceout-link a-text-normal"), href=True)    
    else:
        link = "Not Found"
    return link


def valid_link(link):
    for re_link in RESTRICT_LINKS:
        if link.startswith(re_link):
            return False
    return True


def extract_data(soup):
    if soup:
        all_cards = check_presence(soup.find_all("div", class_="puisg-row"), list_=True)
        for card in all_cards:
            link = get_detail_page_link(card)
            if not valid_link(link):
                continue
            elif link != "Not Found":
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
            soup = ele if ele else ""
        else:
            return       
    return soup
                    

def get_eles_inside_link(soup):
    name = check_presence(soup.find("span", id="title"))
    if not name:
        name = check_presence(soup.find("span", id="productTitle"))
    price = check_presence(get_child_element(soup, "table.a-normal span.a-offscreen")).strip("$")
    if not price:
        price = check_presence(soup.find("span", "a-price aok-align-center reinventPricePriceToPayMargin priceToPay")).strip("$")
    if not price:
        price = check_presence(soup.find("span.apexPriceToPay span.a-offscreen")).strip("$")

    review_ele = soup.find("a", id="acrCustomerReviewLink")
    try:
        review_rating = check_presence(review_ele.find_all("span")[0])
        review_count = check_presence(review_ele.find_all("span")[2])
    except:
        review_rating = ""
        review_count = ""

    if not review_rating:
        rating_ele = soup.find("span",id="acrPopover")
        review_rating = check_presence(rating_ele.find("span","a-size-base a-color-base")) if rating_ele else ""
        review_count = check_presence(review_ele)

    return dict(zip(CSV_HEADERS,(name, price, review_rating, review_count))), soup


def follow_link(link):
    if link:
        res = get_page(link) 
        soup = parse_page(res)
        card_data = get_eles_inside_link(soup)
        return card_data
    else:
        return {}


def group_entity_data(soup,num):
    list_ = []
    for index, (data,soup_) in enumerate(extract_data(soup),start=1):
        if data:
            if not data.get("name"):
                fp = open(f'./{CSV_DIRNAME}/fail-page-{num}-{index}.html', 'w', encoding='utf-8')
                fp.write(str(soup_))
                fp.close()
            list_.append(data)
    return list_

    
def create_csv(domain,data, num):
    if data:
        df = pd.DataFrame(data)
        df.to_csv(f"./{CSV_DIRNAME}/{domain}-page-{num}.csv", index=False)


def parse_url(url):
    if "?" in url:
        if '&' not in url:
            match_ = url.split("?")[-1].split("=")
            keys = [each for index, each in enumerate(match_,start=1) if index % 2 == 1 or index == 1]
            values = [each for index, each in enumerate(match_,start=1) if index % 2 == 0]
            query_params= dict(zip(keys, values))
        else:
            query_str = url.split("?")[-1].split("&")
            match_ = [each.split("=") for each in query_str]
            query_params =dict(match_)
        return query_params
    else:
        return {}

def check_if_next_page(soup):
    if soup:
        pagination_eles = soup.find_all("ul", "a-pagination")
        disabled_next_ele = pagination_eles[-1].find("li","a-disabled a-last") if pagination_eles else ""
        if disabled_next_ele:
            return True

def execute_crawl_stack(url):
    res = get_page(url)
    soup = parse_page(res)
    page_num = parse_url(url).get("page", 1)
    data = group_entity_data(soup, page_num)
    create_csv(DOMAIN, data, page_num)
    if not check_if_next_page(soup):
        follow_next_page(url)
    

def make_url(params):
    params_str = "?"
    for key, value in params.items():
        if params_str == "?":
            params_str= params_str+f"{key}={value}"
        else:
            params_str= params_str+"&"+f"{key}={value}"
    return MAIN_URL+params_str


def follow_next_page(url):
    params = parse_url(url)
    next_page = int(params.get("page", 1)) + 1
    params.update({"page":next_page})
    if next_page == 2:
        params.update({"page":"2"}) 
    url = make_url(params) 
    execute_crawl_stack(url)


def create_dir():
    import os
    if not [each for each in os.walk('.') if 'amazon' in each[0]]:
        os.system(f"mkdir {CSV_DIRNAME}")

if __name__ == '__main__':
    create_dir()
    url = "https://www.amazon.com/s?k=laptops+and+accessories"
    execute_crawl_stack(url)
