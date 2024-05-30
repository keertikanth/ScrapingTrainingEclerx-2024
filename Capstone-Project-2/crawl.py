import requests
import sys
from main import create_url
import os
HEADERS = {
    "User-Agent" : "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Connection": "keep-alive",
    "Retry-After": "5"
}

def get_pagination_details(cat_id):
    url = create_url(cat_id, "1")
    res = requests.get(url, headers=HEADERS, verify=False)
    if res.status_code == 200:
        dict_ = res.json()
        pg_details = dict_.get("pagination")
        return pg_details
    else:
        return {}

def start_crawl():
    pg_details = get_pagination_details(category_id)
    if pg_details:
        total_pages = int(pg_details.get("totalPages"))
        current_page_num = 1
        while current_page_num <= total_pages:
            if TEST and current_page_num > 100:
                break
            os.system(f"python main.py {category_id} {str(current_page_num)}")
            print("Crawling completed")
            current_page_num +=1

    
        

if __name__ == '__main__':
    TEST = True
    category_id = sys.argv[1]
    start_crawl()
    