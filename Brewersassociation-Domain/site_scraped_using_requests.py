import os   
import requests
url = "https://www.brewersassociation.org/wp-content/themes/ba2019/json-store/breweries/breweries.json"

DATA_FILE = "breweries_data.json"
HEADERS = {
    "User-Agent" : "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Connection": "keep-alive",
    "Retry-After": "5"
}

def get_json():
    res = requests.get(url, headers=HEADERS, verify=False)
    if res.status_code == 200:
        return res.json()
    else:
        return [{}]
    
import re

def check(text):
    if not text:
        return ""
    else:
        return text

def parse_json(json_):
    for dict_ in json_:
        data = {}
        data["name"] = check(dict_.get("Name",""))
        data["website"] = check(dict_.get("Website", ""))
        data["phone"] = check(dict_.get("Phone", ""))
        billing_address = dict_.get("BillingAddress", {})
        if billing_address:
            address = check(billing_address.get("street", "")) +", "+ check(billing_address.get("city", "")) + ", " + check(billing_address.get("state", "")) + ", " + check(billing_address.get("country", ""))
            data["address"] = re.sub(r', {2,}', ", ", address)
        else:
            data["address"] = ""
        yield data

import json
def write_data(json_):
    with open(DATA_FILE, 'a+',encoding='utf-8') as fp:
        for index, data in enumerate(parse_json(json_), start=1):
            print(f"Adding data@{str(index)}...")
            if index == 1:
                fp.write("["+"\n")
            if index == len(json_):
                fp.write(json.dumps(data, ensure_ascii=False)+"\n")
                break
            fp.write(json.dumps(data, ensure_ascii=False)+","+"\n")
        fp.write("]")

def delete_file():
    for dir, n, files in os.walk("."):
        for each in files:
            if each == DATA_FILE:
                os.remove(f"./{DATA_FILE}")
                print("file has been deleted...")
        


if __name__ == '__main__':
    delete_file()
    json_ = get_json()
    write_data(json_)
    