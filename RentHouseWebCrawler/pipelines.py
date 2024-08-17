import os
from dotenv import load_dotenv
import pymongo
from itemadapter import ItemAdapter
import logging


class MongoPipeline:
    collection_name = os.getenv("MONGO_COLLECTION")

    def __init__(self, mongo_uri, mongo_port, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_port = mongo_port
        self.mongo_db = mongo_db
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        load_dotenv()
        return cls(
            mongo_uri=os.getenv("MONGO_URI"),
            mongo_port=int(os.getenv("MONGO_PORT")),
            mongo_db=os.getenv("MONGO_DB"),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri, self.mongo_port)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        self.logger.info(f"House added to MongoDB database by {spider.name}!")
        return item
