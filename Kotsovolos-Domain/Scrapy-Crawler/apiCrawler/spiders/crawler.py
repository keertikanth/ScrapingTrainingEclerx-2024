from typing import Iterable
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from apiCrawler.headers import HEADERS
import json
from scrapy.http import Request


class CrawlerSpider(CrawlSpider):
    name = "crawler"
    allowed_domains = ["www.kotsovolos.gr"]
    start_urls = ["https://www.kotsovolos.gr/household-appliances/fridges/fridge-freezers"]

    # rules = (Rule(LinkExtractor(restrict_xpaths=r"Items/"), callback="parse_item", follow=True),)


    def start_requests(self):
        body = {
            "params": "pageNumber=1&pageSize=36&catalogId=10551&langId=-24&orderBy=5",
            "catId" : 35822,
            "storeId": 10151,
            "isCPage":False
            }
        yield Request(url = "https://www.kotsovolos.gr/api/ext/getProductsByCategory?"+"&".join([f"{key}={value}" for key, value in body.items()]),
                      headers=HEADERS,
                      callback=self.parse,
                      )
    
    
    def parse(self, response):
        catalog_entries = response.json().get("catalogEntryView")
        payload_list = self.extract_payload_data(catalog_entries)
        for payload in payload_list:
            if payload:
                for store in self.get_store_info(payload):
                    yield store
                for credit_info in self.get_credit_details(payload):
                    yield credit_info

    def extract_payload_data(self, entries):
        payload_li = []
        for entry in entries:
            data = {}
            data["link"] = entry.get('UserData',[""])[0].get("seo_url")
            data["catId"] = entry.get('uniqueID', '')
            data["storeId"] = entry.get('storeID', '')
            data["nonInstPrice"] = entry.get("price_EUR", "")
            data["currency"]="EUR"
            data["payMethod"] ="CardlinkCreditCard"
            payload_li.append(data)
        return payload_li

    def get_store_info(self, payload):
        payload_={"q":"storeId",
                 "storeId": payload.get("storeId")}
        yield Request(url = "https://www.kotsovolos.gr/api/ext/storeInfoOnline?"+"&".join([f"{key}={value}" for key, value in payload_.items()]), headers=HEADERS, callback=self.parse_store)
    
    def parse_store(self, response):
        return response.json()
    

    def get_credit_details(self, payload):
        payload_= {"catId": payload.get("catId"),
                "payMethod": payload.get("payMethod"),
                "currency" :payload.get("currency"),
                "nonInstPrice": payload.get("nonInstPrice")}
        # import ipdb; ipdb.set_trace()
        yield Request(url ="https://www.kotsovolos.gr/api/ext/getProductCredit?"+"&".join([f"{key}={value}" for key, value in payload_.items()]), headers=HEADERS, callback=self.parse_credit)

    def parse_credit(self, response):
        return response.json()
                
    '''
#creditCard info
catId: 4235001
payMethod: CardlinkCreditCard
currency: EUR
nonInstPrice: 619.00

#store info
q: storeId
storeId: 10151

'''

    

        





    
