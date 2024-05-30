import sys
import requests
from urllib.parse import urljoin
from uuid import uuid4
from database import start_connection,insert_data, DB_NAME
domain_url = "https://www.ajio.com/api/category/"
domain = "https://www.ajio.com/"
options_endpoint = "https://www.ajio.com/api/p/" 

HEADERS = {
    "User-Agent" : "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Connection": "keep-alive",
    "Retry-After": "5"
}

def get_page(url):
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return res.json()
    else:
        return {}

def parse_page(dict_):
    conn, curr = start_connection(DB_NAME)
    products = dict_.get("products")
    for product in products:
        data = {
            "id":str(uuid4()),
            "ajio_id":product.get("code"),
            "name": product.get("name"),
            "website_url": urljoin(domain, product.get("url")),
            "brand": product.get("brandTypeName", ""),
            "category": product.get("brickNameText", ""),
            "segment": product.get("segmentNameText", ""),
            "product_image":[each.get('url') for each in product.get('images')][0] if product.get("images") else "",
            "price": product.get("price", {}).get("value", 0),
            "actual_price" : product.get("wasPriceData", {}).get("value", 0),
            "offer_price": product.get("offerPrice", {}).get("value", 0),
            "option_code": product.get("url").split("/")[-1],
            "option_url": urljoin(options_endpoint,  product.get("url").split("/")[-1])
        }
        try:
            insert_data(curr, data, "PRODUCTS")
            insert_product_data(curr, data)
        except Exception as e:
            print(e)

    conn.commit()
    conn.close()
    
def insert_product_data(curr, data):
    dict_ = get_page(data.get("option_url"))
    name = dict_.get("name")
    status = dict_.get("stock", {}).get("stockLevelStatus", "")
    instock_quantity = dict_.get("stock", {}).get("stockLevel", 0)
    rating_dict = dict_.get("ratingsResponse", {}).get("aggregateRating",{})
    average_rating = float(rating_dict.get('averageRating', '0.0'))
    no_of_ratings = int(rating_dict.get('numUserRatings', '0').replace('.', '').replace('K', '000'))
    product_data = {
        "name": name,
        "id" :data.get("id"),
        "ajio_id":data.get("ajio_id"),
        "status": status,
        "instock_quantity": instock_quantity,
        "avg_rating":average_rating,
        "ratings_count":no_of_ratings
    }
    insert_data(curr, product_data, "PRODUCT")



def create_url(category_id, page_num):
    url = domain_url+category_id+f"?currentPage={page_num}"
    return url



if __name__ == '__main__':
    category_id = sys.argv[1]
    page_num = sys.argv[2]
    url = create_url(category_id, page_num)
    print(url)
    dict_ = get_page(url)
    parse_page(dict_)



