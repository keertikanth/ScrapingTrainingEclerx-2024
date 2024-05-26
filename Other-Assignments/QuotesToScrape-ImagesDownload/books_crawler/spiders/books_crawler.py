import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class BooksSpider(CrawlSpider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    rules = (Rule(LinkExtractor(deny_domains=("google.com",)),callback='start_scrapping',follow=True),)
    # rules = (Rule(LinkExtractor(deny=("fiction",)),callback='start_scrapping',follow=True),)
    # rules = (Rule(LinkExtractor(allow=("fiction",), deny=("Romance,")),callback='start_scrapping',follow=True),)


    def parse(self, response):
        pass


    def start_scrapping(self, response):
        pass
