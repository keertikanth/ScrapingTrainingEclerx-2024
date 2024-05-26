
import requests
from bs4 import BeautifulSoup as bs
import json
from copy import deepcopy
import time
from pprint import pprint
import pandas as pd
import time
import math




HEADERS = {
    "User-Agent" : "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Connection": "keep-alive",
    "Retry-After": "5"
}

query_str_cat = "searchResultDTOMobile > searchResultDTO > matchingCategories > subCategories > subCategories"

query_str = "searchResultDTOMobile > catalogSearchDTOMobile"




def load_cat_info():
    dict_ = json.load(open('snapdeal_2.json', 'r'))
    copy_dict = deepcopy(dict_)
    return copy_dict



def get_search_results_url(res):
    cookies = res.cookies
    url = f"""https://m.snapdeal.com/service/get/search/v3/getSearchResults?responseProtocol=PROTOCOL_JSON&requestProtocol=PROTOCOL_JSON&apiKey=snapdeal&zone=&keyword=&categoryId=&categoryXPath=&start=&number=&sortBy=plrty&checkServiceable=true&pincode=&q=&spellCheck=&sdId={cookies.get('u')}&eId=&onDemand=true&pagetype=clp&response_type=similar_ad&fetchGuides=true&searchStateV2=null&config=voiceSearch%3Afalse&slotId=sd-cr-search-0-12&slotName=24&siteId=102&websiteId=2&publisherId=1&serveAds=true&showSimilarAds=false"""
    return url

def get_cookies():
    return res.cookies

def write_cat_info():
    cookies = get_cookies()
    KITCHEN_XPATH = "appliances-kitchen"
    url = f"""https://m.snapdeal.com/service/get/search/v3/getSearchResults?responseProtocol=PROTOCOL_JSON&requestProtocol=PROTOCOL_JSON&apiKey=snapdeal&zone=&keyword=&categoryId=&categoryXPath={KITCHEN_XPATH}&start=0&number=12&sortBy=plrty&checkServiceable=true&pincode=&q=&spellCheck=&sdId={cookies.get('u')}&eId=&onDemand=true&pagetype=clp&response_type=similar_ad&fetchGuides=true&searchStateV2=null&config=voiceSearch%3Afalse&slotId=sd-cr-search-0-12&slotName=24&siteId=102&websiteId=2&publisherId=1&serveAds=true&showSimilarAds=false"""
    res = requests.get(url, headers=HEADERS)
    with open('snapdeal_2.json', 'wb+') as fp:
        fp.write(res.content)


def remove_extra_lists(list_):
    if list_ and len(list_)==1:
        if isinstance(list_[0], list):
            return list_[0]
        else:
            return list_

def extract(cp_dict, index=0):
    query_list = query_str_cat.split(">")

    if len(query_list) <= index:
        return cp_dict
    for index, each in enumerate(query_list[index:],start=index):
        if each:
            query_res = cp_dict.get(each.strip())
            if len(query_list) < 2 and query_res:
                return query_res
            if query_res:
                if isinstance(query_res, list):
                    list_ = [extract(each, index=index+1) for each in query_res ]
                    return list_
                    
                elif isinstance(query_res, dict):
                    return extract(query_res, index=index+1)
                
def cleaned_category_data():
    all_=extract(copy_dict) 
    while len(all_) == 1:
        if isinstance(all_[0], list):
            all_= all_[0]
        else:
            return all_        
    return all_


def extract_category_data(res):
    category_data = []
    for each in res:
        data = {}
        data["snapdeal_cat_id"] = each.get("id")
        data["name"] = each.get("name")
        data["link"] = each.get("link")
        data["no_of_results"] = each.get("noOfResults")
        category_data.append(data)
    return category_data

def get_data(cat_data,res):
    for data in cat_data:
        get_each_data(data, res)

def get_each_data(payload, res):
    COUNT =0
    FLAG=True
    while COUNT <=int(payload.get("no_of_results"))+50 and FLAG:
        page_num = int(COUNT / 50)
        print(f"Extracting {payload.get('link')} - page {page_num+1}")
        url = get_search_results_url(res)
        url_ = url.replace("categoryXPath=", f'categoryXPath={payload.get("link")}')
        url_ = url_.replace("&start=",f"&start={COUNT}")
        if int(payload.get("no_of_results"))+50 - COUNT >= 50:
            url_= url_.replace("&number=","&number=50")
        else:
            url_= url_.replace("&number=",f"&number={str(int(payload.get('no_of_results')) % 50)}")
            FLAG=False
        res = requests.get(url_, headers=HEADERS)
        with open(f'./snapdeal_v4/{payload.get("link")}-{page_num+1 if page_num else "1"}.json', 'wb+') as fp:
            fp.write(res.content)
            COUNT +=50
            print("Crawling Done")
            time.sleep(2)



def check_data(name, page_list):
    global query_str_cat
    query_str_cat = query_str
    for page_num in page_list:
        dict_ = json.load(open(f'./snapdeal_data/{name}-{page_num}.json', 'r'))
        res=extract(dict_)
        pprint([f"name:{each.get('title')}, price:{each.get('price')}"+"\n" for each in cleaned_category_data(all_=res)])

def extract_from_json(payload_li):
    global query_str_cat
    query_str_cat = query_str
    for each in payload_li:
        no_of_res = int(each.get("no_of_results"))
        no_of_pages = math.ceil(no_of_res/50)
        name = each.get("link")
        all_ = []
        for page_num in range(1,no_of_pages+1):
            dict_ = json.load(open(f'./snapdeal_v4/{name}-{page_num}.json', 'r'))
            catalog_list = extract(dict_)
            data = extract_final_data(catalog_list)
            all_ = all_ + data
        create_csv(all_, name)
        print("Converted into Csv", name)


def create_csv(all_, name):
    df = pd.DataFrame(all_)
    df.to_csv(f"./snapdeal_final_v2/{name}.csv", index=False)
    
    
def extract_final_data(list_):
    all_= []
    for dict_ in list_:
        data = {}
        data["product_name"]=dict_.get("title")
        data["price"] = dict_.get("price")
        data["images"] = dict_.get("imgs")
        all_.append(data)
    return all_
    
def extract_category_data(res):
    category_data = []
    for each in res:
        data = {}
        data["snapdeal_cat_id"] = each.get("id")
        data["name"] = each.get("name")
        data["link"] = each.get("link")
        data["no_of_results"] = each.get("noOfResults")
        category_data.append(data)
    return category_data



def get_data(payload_li, res):
    for payload in payload_li:
        print(payload)
        get_each_data(payload, res)


if __name__ == '__main__':
    url = "https://m.snapdeal.com"
    res = requests.get(url,headers=HEADERS)
    copy_dict = load_cat_info()
    cat_data_cleaned=cleaned_category_data()
    payload_list=extract_category_data(cat_data_cleaned)
    get_data(payload_list, res)
    extract_from_json(payload_list)
    payload_list=extract_category_data(payload_list)

