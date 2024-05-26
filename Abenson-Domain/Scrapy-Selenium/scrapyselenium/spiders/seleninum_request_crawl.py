import scrapy
from scrapy_selenium import SeleniumRequest

CSV_HEADERS = ("name", "price", "status")

class SeleninumRequestCrawlSpider(scrapy.Spider):
    name = "seleninum_request_crawl"
    allowed_domains = ["www.abenson.com"]
    start_urls = ["https://www.abenson.com/mobile/smartphone.html"]

    def start_requests(self):
        yield SeleniumRequest(url="https://www.abenson.com/mobile/smartphone.html",
                              wait_time=10,
                              callback=self.parse,
                              )
        
    def parse(self, response):
        links = response.xpath('//div[@class=" gallery-items"]/div[@class=" item-siminia-product-grid-item-3do siminia-product-grid-item "]/descendant::a/@href').extract()
        for link in links[:10]:
            print(link)
            url = "https://"+self.allowed_domains[0]+link
            data = SeleniumRequest(url= url, callback=self.parse_link)
            yield data

    def parse_link(self, response):
        details_ele = response.css("div#product-detail form")
        if details_ele:
            name = details_ele[0].css("h1::text").get()
            price = details_ele[0].css("span.productFullDetail-regularPrice-188 span::text").extract()
            price = "".join(price) if price else ""
            status = details_ele[0].css("div.stockStatus-status-2Bj::text").get()
            yield dict(zip(CSV_HEADERS,(name, price, status)))
        else:
            yield {}
