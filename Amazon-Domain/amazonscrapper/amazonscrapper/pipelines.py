# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import sqlite3


class AmazonscrapperPipeline:
    def __init__(self):
        self.create_conn()
        self.create_table()
 
    
    def create_conn(self):
        self.conn = sqlite3.connect("amazonscrappertest.db")
        self.curr = self.conn.cursor()

    def create_table(self):
        self.curr.execute("""DROP TABLE IF EXISTS test_tableV2""")
        self.curr.execute("""create table test_tableV2(
                        name text,
                        price text,
                        avg_review_rating text,
                        review_count text
                        )""") 
 
    def process_item(self, item, spider):
        self.insert_item(item)
        return item
 
    def insert_item(self, item):
        self.curr.execute("""insert into test_table values (?,?,?,?)""", (
            item.get("name", ""),
            item.get("price", ""),
            item.get("avg_review_rating", ""),
            item.get("review_count", "")
        ))
        self.conn.commit()

    def close_spider(self, spider):
        self.curr.close()
        self.conn.close()
