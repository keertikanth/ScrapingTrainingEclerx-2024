import requests
import pandas as pd



HEADERS = {
    "User-Agent" : "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Connection": "keep-alive",
    "Retry-After": "5"
}

def get_json():
    url = "https://recommendationv2.api.useinsider.com/v2/most-valuable?"
    params= {
    "details": "true",
    "locale": "th_TH",
    "partnerName": "10008685",
    "size": "100",
    "currency": "THB",
    "categoryList": '["NOTEBOOK", "Notebook"]',
    "filter": '([in_stock][>=][0])'
    }
    params_str = "&".join([f"{key}={value}" for key, value in params.items()])
    url = url + params_str
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return res.json()
    else:
        return {}

def extract_data(dict_):
    data_li = dict_.get("data")
    all_ = []
    for data in data_li:
        temp = {}
        temp['name'] = data.get("name","")
        temp['in_stock'] = data.get("in_stock", 0)
        temp['price'] = data.get("price", {}).get("THB", 0)
        temp['image_url'] = data.get("image_url","")
        temp['item_id'] = data.get("item_id", "")
        all_.append(temp)
    return all_


def create_csv(all_, name):
    df = pd.DataFrame(all_)
    df.to_csv(f"{name}.csv", index=False)


if __name__ == '__main__':
    name = "advice_data"
    dict_ = get_json()
    all_ = extract_data(dict_)
    create_csv(all_,name)
    
    