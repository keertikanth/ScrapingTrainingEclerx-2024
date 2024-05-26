import scrapy
from scrapy.http import Request
from ..items import BooksCrawlerItem
import re

HTTP_PROTOCOL='https://'
class BooksScraperSpider(scrapy.Spider):
    name = "books_scraper"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]
    items = BooksCrawlerItem()

    def parse(self, response):
        books_url = response.xpath("//ol[@class='row']//article[@class='product_pod']//h3/a/@href").extract()

        # Method 1 - using list comprehension

        # Method 2
        for book_url in books_url:
            yield Request(response.urljoin(book_url), callback=self.parse_book)

        # Logic to navigate to Next Page
            
        try:
            nextpage_url = response.xpath("//li[@class='next']/a[contains(text(),'next')]/@href").get()
            if nextpage_url is not None:
                yield Request(response.urljoin(nextpage_url))
        except:
            self.logger.info("----------------------No more pages to scrape----------------------")

    def parse_book(self,response):
        # Scrape the individual books wrt datapoints
        # import ipdb; ipdb.set_trace()
        book_title = response.xpath("//div[@class='col-sm-6 product_main']/h1/text()").get()
        book_price = response.xpath("//div[@class='col-sm-6 product_main']/p[@class='price_color']/text()").get()
        # book_rating = response.xpath("//div[@class='col-sm-6 product_main']/p[@class='star-rating Three']/@class").get()

        book_rating = response.xpath("//div[@class='col-sm-6 product_main']/p[contains(@class,'star-rating')]/@class").get()
        image_url_rel = response.xpath("//div[@class='carousel-inner']//img/@src").get()
        image_url_abs= re.sub(r'(\.{2}\/){1,}','/',image_url_rel)
        image_url = f"{HTTP_PROTOCOL}{self.allowed_domains[0]}{image_url_abs}"

        # yield {"Book Title" : book_title, "Book Price" : book_price, "Book Rating" : book_rating}

        BooksScraperSpider.items['BookPrice'] = book_price
        BooksScraperSpider.items['BookTitle'] = book_title
        BooksScraperSpider.items['BookRating'] = book_rating
        BooksScraperSpider.items["image_urls"] = [image_url]

        yield BooksScraperSpider.items

