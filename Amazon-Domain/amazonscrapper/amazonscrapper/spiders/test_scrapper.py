import scrapy
from scrapy import Selector
from amazonscrapper.items import AmazonscrapperItem
import re

CSV_HEADERS = ("name", "price", "avg_review_rating", "review_count")
HTTP_PROTOCOL= "https://"
DOMAIN = "www.amazon.com"

class TestScrapperSpider(scrapy.Spider):
    name = "test_scrapper"
    allowed_domains = ["www.amazon.com"]
    start_urls = ["https://www.amazon.com/s?k=laptops+and+accessories"]
    page_num = 1


    def parse(self, response):
        all_cards = response.xpath("//div[@class='puisg-row']").getall()
        for card in all_cards[:10]:
            link_section = Selector(text=card).xpath("//div[@class='a-section a-spacing-small a-spacing-top-small puis-padding-right-small']").get()
            if link_section:
                link = Selector(text=link_section).xpath("//a[@class='a-link-normal s-faceout-link a-text-normal']/@href").get()
                # import ipdb; ipdb.set_trace()
                if not link.startswith("/sspa"):
                    yield response.follow(url=HTTP_PROTOCOL+DOMAIN+link, callback=self.parse_page)
    
        disabled_next_ele = response.xpath("//ul[@class='a-pagination']/descendant::li[@class='a-disabled a-last']").get()
        if not disabled_next_ele:
            if self.page_num==1:
                yield response.follow(url=response.url+"&page=2", callback=self.parse)
            else:
                yield response.follow(url=re.sub(r'\d+$',str(self.page_num+1),response.url), callback=self.parse)
            self.page_num +=1
            
    
    def parse_page(self, response):
        item = AmazonscrapperItem()
        name = response.css("span#title::text").get(default="")
        if not name:
            name = response.css("span#productTitle::text").get(default="")
        price = response.css("table.a-normal span.a-offscreen::text").get(default="").strip("$")
        if not price:
            price = response.css("span.a-price.aok-align-center.reinventPricePriceToPayMargin.priceToPay::text").get(default="").strip("$")
        review_ele = response.css("a#acrCustomerReviewLink").get()
        try:
            review_rating = Selector(text=review_ele).xpath("//span/text()").getall()[0].strip()
            review_count =  Selector(text=review_ele).xpath("//span/text()").getall()[-1].strip()
        except:
            review_rating = ""
            review_count = ""

        item["name"] = name
        item["price"] = price
        item["avg_review_rating"] = review_rating
        item["review_count"] = review_count
        # yield dict(zip(CSV_HEADERS,(name, price, review_rating, review_count)))
        yield item
        
