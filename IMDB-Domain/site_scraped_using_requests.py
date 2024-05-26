import requests
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
HEADERS = {
    "User-Agent" : "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Connection": "keep-alive",
    "Retry-After": "5"
}

url = "https://www.imdb.com/chart/top"


def get_soup():
    response = requests.get(url, headers=HEADERS, verify=False)
    import ipdb; ipdb.set_trace()
    if response.status_code:
        soup = bs(response.text, 'html.parser')
        return soup
    
def check_presence(ele):
     if ele:
        return ele.text
     else:
          return ""
          
csv_headers = ("name", "rank", "year")

def extract_data(soup):
    final_data = []
    all_ = soup.find('ul', 'ipc-metadata-list').find_all("li")
    for each in all_:
        name = re.sub(r'^\d*\.','',check_presence(each.find('h3','ipc-title__text'))).strip()
        rank_li = re.findall(r'\d\.\d',check_presence(each.find('span', 'ipc-rating-star')))
        rank = rank_li[0]  if rank_li else ""
        year = check_presence(each.find('span', class_="sc-b189961a-8 kLaxqf cli-title-metadata-item"))
        final_data.append(dict(zip(csv_headers,(name, rank, year))))
    return final_data


def create_csv(final_data):
    df = pd.DataFrame(final_data)
    df.to_csv('top-250-imdb_new.csv', index=False)


if __name__ == '__main__cd ':
    soup = get_soup()
    final_data = extract_data(soup)
    create_csv(final_data)