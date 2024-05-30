## About
This project is based on scraping ajio website given a category such as T-shirts is chosen and collected the useful data such product price , rating , images using ajio internal api

Due to the use of the internal api, this data for this project is easily crawled

## Control Flow

Created two tables  
A:PRODUCTS points to all-products page (i.e https://www.ajio.com/api/category/830216014) which holds the data for all the products in that category
B:PRODUCT points to information gathered from a single-product page

## PRODUCTS:
    ajio_id             (product-code)
    name                (product-name)
    website_url         (product-display-url)
    brand               (product-brand)
    category            (product-category)
    segment             (product-segment)
    product_image       (product-image)
    price               (product-sale-price)
    actual_price        (product-initial-price)
    offer_price         (product-offer-price)
    option_code         (detail-page-code)
    option_url          (detail-page-link)
## PRODUCT:
    id                  (foreign-key PRODUCTS id)
    ajio_id             (foreign-key PRODUCTS ajio_id),
    name                (product-name),
    status              (product-instock-status),
    instock_quantity    (product-instock-quantity)
    avg_rating          (product-rating)
    ratings_count       (product-rating-count)

database.py will create the required database, crawl.py will initiate the crawling process by setting up category id and provide parameters such as category id and page number to the main.py

main.py will scrape the data from the products page and also gets the individual product page using requests library

For testing purposes, script is modified to scrape 100 pages of all products page
        


    




