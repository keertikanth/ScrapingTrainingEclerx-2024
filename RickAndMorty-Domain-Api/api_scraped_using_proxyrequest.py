import requests
import os
from time import sleep
import pandas as pd
import json
from zyte_api import ZyteAPI
from base64 import b64decode

domain = "https://rickandmortyapi.com/api"
endpoint = "/character/"
CSV_FOLDER = "rickandmortyapi"
HEADERS = {
    "User-Agent" : "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Accept":"application/json; charset=utf-8",
}


def get_page_using_proxy(url):
    api_response = requests.post(
        "https://api.zyte.com/v1/extract",
        auth=("<APIKEY>", ""),
        json={
            "url": url,
            "httpResponseBody": True,
        },
    )
    http_response_body: bytes = b64decode(
        api_response.json()["httpResponseBody"])
    if http_response_body:
        return json.loads(http_response_body)
    else:
        return ""


def get_page_json(page_num):
    url = domain+endpoint+f"?page={page_num}"
    data = {}
    data["page_num"] = page_num
    print(f"Crawling-{page_num} Started")
    response = get_page_using_proxy(url)
    if response:
        data.update({'response':response})
        return data
    else:
        return data
    
def parse_response(data):
    page_data = []
    if data.get('response'):
        results = data.get('response', {}).get("results", [])
        for result in results:
            temp = {}
            temp["name"] = result.get("name", "")
            temp["episodes"] = result.get("episode", [])
            temp["page_num"] = data.get("page_num")
            page_data.append(temp)
        del data["response"]
    data.update({"page_data":page_data})
    return data
    

def get_page_count():
    url = domain+endpoint
    response = get_page_using_proxy(url)
    count = response.get("info", {}).get("pages", 0)
    if count:
        return int(count)
    else:
        return 0


def create_csv(parsed_data):
    if parsed_data.get("page_data"):
        df = pd.DataFrame(parsed_data.get("page_data"))
        df.to_csv(f"./{CSV_FOLDER}/{parsed_data.get('page_num')}.csv", index=False)
        
        
def create_dir():
    if not [each for each in os.walk('.') if f'{CSV_FOLDER}' in each[0]]:
        os.system(f"mkdir {CSV_FOLDER}")

def get_data():
    create_dir()
    count = get_page_count()
    if count:
        for page_num in range(1, count+1):
            init_data = get_page_json(str(page_num))
            parsed_data = parse_response(init_data)
            create_csv(parsed_data)


if __name__ == '__main__':
    get_data()

