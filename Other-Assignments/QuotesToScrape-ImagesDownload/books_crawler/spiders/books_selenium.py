from typing import Iterable
import scrapy
from scrapy.selector import Selector
from scrapy.http import Request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

options = webdriver.ChromeOptions()
options.add_argument('--headless')

class BooksSeleniumSpider(scrapy.Spider):
    name = "books_selenium"
    allowed_domains = ["books.toscrape.com"]
    # start_urls = ["https://books.toscrape.com/"]
    base_url = "https://books.toscrape.com/"

    ## generate our initial requests dynamically
    def start_requests(self):
        # self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options = options)
        self.driver = webdriver.Chrome()
        self.driver.get("https://books.toscrape.com/")
        
        sel = Selector(text=self.driver.page_source)

        # Extract all the book urls
        books_urls = sel.xpath("//h3/a/@href").get()

        for book_url in books_urls:
            url = BooksSeleniumSpider.base_url + book_url
            yield Request(url, callback=self.parse)


        

        while True:     
            try:
                ## Move to next page by cicking on next button with selenium click method

                next_page = self.driver.find_element(By.XPATH, "//li[@class='next']/a[@href]")
                self.logger.info("Waiting for 3 seconds...")
                time.sleep(3)
                next_page.click()
                books_urls = sel.xpath("//h3/a/@href").get()

                for book_url in books_urls:
                    
                    url = BooksSeleniumSpider.base_url + book_url
                    yield Request(url, callback=self.parse)

            except NoSuchElementException:
                self.logger.info("No more pages to crawl!!!")
                self.driver.quit()
                break
 

    def parse(self, response):
        # Extract Book Title and Book Page URL
        #### The selector for book title is not working
        # book_title  = response.xpath("//div[@class='col-sm-6 product_main']/h1/text()").get()
        book_title  = response.xpath("//h1/text()").get()
        book_page_url = response.request.url
        

        yield {'Book Title' : book_title,
               'Book Page URL' : book_page_url}
        

    # def close(self,reason):
    #     # put any code that needs to be run when spider is closed
    #     if reason == 'finished':
    #         self.driver.quit()
    #         self.driver.close()
    #         print('-----------------Spider has finished execution-----------------') 
    #     elif reason == 'cancelled':
    #         self.driver.quit()
    #         self.driver.close()
    #         print('-----------------Spider has been cancelled-----------------')

    #     else:
    #         self.driver.quit()
    #         self.driver.close()
    #         print('-----------------Spider has encountered error-----------------')

    def spider_closed(self, reason, spider):
        # put any code that needs to be run when spider is closed
        if reason == 'finished':
            self.driver.quit()
            self.driver.close()
            print('-----------------Spider has finished execution-----------------') 
        elif reason == 'cancelled':
            self.driver.quit()
            self.driver.close()
            print('-----------------Spider has been cancelled-----------------')

        else:
            self.driver.quit()
            self.driver.close()
            print('-----------------Spider has encountered error-----------------')


         
