import scrapy
import re

HTTP_PROTOCOL= "https://"
DOMAIN = "webscraper.io"
CSV_HEADERS = ("name", "price", "review")

class Scrapperversion1Spider(scrapy.Spider):
    name = "ScrapperVersion1"
    allowed_domains = ["webscraper.io"]
    start_urls = ["https://webscraper.io/test-sites/e-commerce/static/computers/tablets"]

    def parse(self, response):
        links = response.xpath("//a[@class='title']/@href").extract()
        for link in links:
            yield response.follow(url=HTTP_PROTOCOL+DOMAIN+link, callback=self.parse_link)

        if response.xpath("//li/a[@rel='next']"):
            url = response.xpath("//li/a[@rel='next']/@href").get()
            yield response.follow(url=url, callback=self.parse)


    def parse_link(self, response):
        name = response.xpath("//div[@class='caption']/h4[@class='title card-title']/text()").get()
        price = response.xpath("//div[@class='caption']/h4[@class='price float-end pull-right']/text()").get().strip("$")
        review = re.sub(r'[\t\n]', "",response.xpath("//div[@class='ratings']/p[@class='review-count']/text()").get())
        review = int(re.match(r'^\d+',review).group())
        yield dict(zip(CSV_HEADERS, (name, price, review)))