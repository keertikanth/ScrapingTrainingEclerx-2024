import scrapy
from selenium import webdriver
from time import sleep, time
from scrapy import Selector
from selenium.webdriver.common.by import By


HTTP_PROTOCOL = "https://"
CSV_HEADERS = ("name", "price", "status")

class SeleniumCrawlSpider(scrapy.Spider):
    name = "selenium_crawl"
    allowed_domains = ["www.abenson.com"]
    start_urls = ["https://www.abenson.com/mobile/smartphone.html"]

    def start_requests(self) :
        self.driver = webdriver.Chrome()
        self.driver.get(SeleniumCrawlSpider.start_urls[0])
        self.check_items_exist(self.driver)
        self.html = self.driver.page_source
        self.driver.close()
        return super().start_requests()
    
    def check_ele_exist(self, xpath, driver):
    
        start = time()
        while True:
            if time()-start < 5:
                try:
                    ele = driver.find_elements(By.XPATH, xpath)
                    if ele:
                        return 
                except:
                    pass
            else: 
                break


    def check_items_exist(self, driver):
        self.check_ele_exist('//div[@class=" gallery-items"]/div[@class=" item-siminia-product-grid-item-3do siminia-product-grid-item "]/descendant::a', driver)
        
    
            
    def check_target_exist(self, driver):
        self.check_ele_exist("//div[@id='product-detail']//form", driver)
                    
        
    def follow_link(self, link,callable=""):
        driver = webdriver.Chrome()
        driver.get(f"{HTTP_PROTOCOL}{SeleniumCrawlSpider.allowed_domains[0]}{link}")
        self.check_target_exist(driver)
        ps = driver.page_source
        driver.close()
        if callable:
            data = callable(ps)
        return data

    def parse(self, response):
        html = Selector(text=self.html)
        links = html.xpath('//div[@class=" gallery-items"]/div[@class=" item-siminia-product-grid-item-3do siminia-product-grid-item "]/descendant::a/@href').extract()
        for link in links[:10]:
            data = self.follow_link(link, callable=self.parse_link)
            yield data

    def parse_link(self, ps):
        html = Selector(text=ps)
        details_ele = html.css("div#product-detail form")
        if details_ele:
            name = details_ele[0].css("h1::text").get()
            price = details_ele[0].css("span.productFullDetail-regularPrice-188 span::text").extract()
            price = "".join(price) if price else ""
            status = details_ele[0].css("div.stockStatus-status-2Bj::text").get()
            yield dict(zip(CSV_HEADERS,(name, price, status)))
        else:
            yield {}



        
