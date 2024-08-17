import os
import redis
import pymongo
from dotenv import load_dotenv


def push_urls(redis_host, redis_port, spider_name, urls):
    # Connect to the Redis server
    r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

    # Push each URL to the Redis queue for the given spider
    for url in urls:
        r.lpush(f'{spider_name}:start_urls', url)
        print(f"Pushed {url} to {spider_name}:start_urls")


if __name__ == "__main__":
    # Clear mongoDB
    load_dotenv()
    client = pymongo.MongoClient(os.getenv('MONGO_URI'),
                                 int(os.getenv('MONGO_PORT')))
    db = client[os.getenv('MONGO_DB')]
    db.drop_collection(os.getenv('MONGO_COLLECTION'))

    # Configure your Redis connection and spider names
    redis_host = os.getenv('REDIS_HOST')
    redis_port = os.getenv('REDIS_PORT')

    # Spider 1
    spider_name_1 = 'ddroom'
    urls_1 = [
        'https://api.dd-room.com/api/v1/search?category=house&order=recommend&sort=desc&page=1',
        # Add more URLs as needed
    ]

    # Spider 2
    spider_name_2 = 'rakuya'
    urls_2 = [
        f'https://www.rakuya.com.tw/rent/rent_search?search=city&city={cnt}&upd=1'
        for cnt in range(21)
    ]

    # Clear redis
    r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    r.delete(f'{spider_name_1}:start_urls')
    r.delete(f'{spider_name_2}:start_urls')
    # Push URLs to Redis
    push_urls(redis_host, redis_port, spider_name_1, urls_1)
    push_urls(redis_host, redis_port, spider_name_2, urls_2)
