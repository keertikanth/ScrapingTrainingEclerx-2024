from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
from scrapy import Selector
import time
import json



XPATH_FILE = "SELENIUM_XPATHS"
COUNT = 0
CSV_HEADERS = ("name", "price", "status")


def read_xpaths_file():
    with open(XPATH_FILE, 'r') as fp:
        str_ = fp.read()
        if str_:
            dict_items = [each.split("=>") for each in str_.split("\n")]
            return dict(dict_items)
        else:
            return {}


def extract_links(items):
    links = []
    for item in items[COUNT:]:
        links.append(item.get_attribute("href"))
    return links


def text(str_):
    if str_:
        soup = bs(str_,'html.parser')
        return soup.text


def get_elements(html):
    details_ele = html.css("div#product-detail form")
    if details_ele:
        name = text(details_ele[0].css("h1").get())
        price = text(details_ele[0].css("span.productFullDetail-regularPrice-188").get())
        status = text(details_ele[0].css("div.stockStatus-status-2Bj").get())
        return dict(zip(CSV_HEADERS,(name, price, status)))


def sleep_until(driver):
    count=0
    FLAG=True
    while FLAG:
        soup = bs(driver.page_source, 'html.parser')
        ele = soup.find("h1", "productFullDetail-productName-2jb")
        FLAG = False if ele else True
        if FLAG:
            time.sleep(1)
            count +=1
            if count > 5:
                break
        else:
            break

def create_new_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    return driver
    
FLAG=True
    
def follow_link(link):
    global FLAG
    driver = create_new_driver()
    driver.get(link)
    sleep_until(driver)
    ps = driver.page_source
    html = Selector(text=ps)
    data = get_elements(html)
    driver.close()
    return data


def count_items(ps):
    count = len(ps)
    return count



def scroll_page(driver):
    global COUNT
    time.sleep(10)
    count = 0
    items_count = count_items(driver.page_source)
    while count < items_count:
        count = items_count
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        while items_count == count:
            items_count = count_items(driver.page_source)
            time.sleep(1)
        COUNT += 1
        if COUNT > 2:
            break
        
    

def extract_links_frm_main_pg(xpaths):
    driver = create_new_driver()
    driver.get(url)
    scroll_page(driver)
    time.sleep(1)
    items = driver.find_elements(By.XPATH, xpaths.get("ITEMS"))
    if items:
        links = extract_links(items)
        driver.close()
        return links
    else:
        driver.close()
        return []
    

    
def export_data_from_links(links):
    add_data("[")
    for link in links:
        data = follow_link(link)
        add_data(data)
    add_data("]")



def add_data(data):
    with open('abenson_data.json', 'a+') as fp:
        if isinstance(data, str):
            fp.write(data)
        else:
            fp.write(json.dumps(data)+"\n")


if __name__ =='__main__':
    url ="https://www.abenson.com/mobile/smartphone.html"
    xpaths = read_xpaths_file()
    links = extract_links_frm_main_pg(xpaths)
    print(xpaths)
    export_data_from_links(links)
    



