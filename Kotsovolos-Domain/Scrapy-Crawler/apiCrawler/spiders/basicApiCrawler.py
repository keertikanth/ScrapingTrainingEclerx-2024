import scrapy
from apiCrawler.headers import HEADERS

'''
Payloads

#creditCard info
catId: 4235001
payMethod: CardlinkCreditCard
currency: EUR
nonInstPrice: 619.00

#store info
q: storeId
storeId: 10151

'''


class BasicapicrawlerSpider(scrapy.Spider):
    name = "basicApiCrawler"
    allowed_domains = ["www.kotsovolos.gr"]
    start_urls = ["http://www.kotsovolos.gr/household-appliances/fridges/fridge-freezers"]

    def start_requests(self):
        body = {
            "params": "pageNumber=1&pageSize=36&catalogId=10551&langId=-24&orderBy=5",
            "catId" : 35822,
            "storeId": 10151,
            "isCPage":False
            }
        yield scrapy.Request(url = "https://www.kotsovolos.gr/api/ext/getProductsByCategory?"+"&".join([f"{key}={value}" for key, value in body.items()]),
                      headers=HEADERS,
                      callback=self.parse
                      )
    
    
    def extract_payload_data(self, entries):
        payload_li = []
        for entry in entries:
            data = {}
            data["link"] = entry.get('UserData',[""])[0].get("seo_url")
            data["main_data"] = {'name':entry.get("name"), 'price':entry.get("price_EUR", ""),
                                 "short_description": entry.get("shortDescription", "")}
            data["catId"] = entry.get('uniqueID', '')
            data["storeId"] = entry.get('storeID', '')
            data["nonInstPrice"] = entry.get("price_EUR", "")
            data["currency"]="EUR"
            data["payMethod"] ="CardlinkCreditCard"
            payload_li.append(data)
        return payload_li
    

    def parse(self, response):
        catalog_entries = response.json().get("catalogEntryView")
        payload_list = self.extract_payload_data(catalog_entries)
        for payload in payload_list:
            if payload:
                meta = {"payload": payload,
                        "main_data": payload.get("main_data")}
                payload_={"q":"storeId",
                        "storeId": payload.get("storeId")}
                yield response.follow(url="https://www.kotsovolos.gr/api/ext/storeInfoOnline?"+"&".join([f"{key}={value}" for key, value in payload_.items()]), headers=HEADERS, callback=self.parse_store, meta=meta, dont_filter =True)
                
           
    def parse_store(self, response):
        meta = response.request.meta
        payload = meta.get("payload")
        payload_= {"catId": payload.get("catId"),
                "payMethod": payload.get("payMethod"),
                "currency" :payload.get("currency"),
                "nonInstPrice": payload.get("nonInstPrice")}
        dict_ = response.json()
        data = {}
        #get store data
        data["storeIdentifier"] = dict_.get("resultList",[{}])[0].get("identifier")
        data["storeLocation"] = dict_.get("resultList",[{}])[0].get("locationInfo")
        meta.update({'store_data':data})
        yield response.follow(url ="https://www.kotsovolos.gr/api/ext/getProductCredit?"+"&".join([f"{key}={value}" for key, value in payload_.items()]), \
                              headers=HEADERS, callback=self.parse_credit, meta=meta)
    

    def parse_credit(self, response):
        meta = response.request.meta
        dict_ =  response.json()
        data = {}
        #get credit data
        data["installment_options"] = dict_.get("installmentOptions", [""])[0]
        final_data = {}
        final_data.update({
            'main_data':meta.get('main_data'),
         'store_data': meta.get('store_data'),
         'credit_data':data
         })
        return final_data
    
