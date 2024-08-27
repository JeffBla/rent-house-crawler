from collections import defaultdict
from scrapy_redis.spiders import RedisSpider

from RentHouseWebCrawler.items import RentalItem


class RentalSpider_ddroom(RedisSpider):
    name = 'ddroom'
    allowed_domains = ['api.dd-room.com',
                       'dd-room.com']  # Replace with the actual domain
    redis_key = f'{name}:start_urls'

    def __init__(self, *args, **kwargs):
        super(RentalSpider_ddroom, self).__init__(*args, **kwargs)
        # Your custom initialization logic
        self.obejct_start_url = 'https://www.dd-room.com/object/'

    def parse(self, response):
        # Extract house listings
        house_list = response.json()['data']['search']['items']
        # cover image
        self.house_imgUrls = list(
            map(lambda x: x['covers'][0]['image']['md'], house_list))
        self.house_page = list(
            map(lambda x: self.obejct_start_url + x['object_id'], house_list))

        # house info
        for idx in range(len(self.house_page)):
            house = self.ParseHouse(idx, house_list[idx])
            yield house

        # next page
        # Follow pagination links
        num_pages = response.json()['data']['search']['last_page']
        for (i) in range(2, num_pages + 1):
            next_page = f'https://api.dd-room.com/api/v1/search?category=house&order=recommend&sort=desc&page={i}'
            self.logger.info(f'Next page: {next_page}')
            # push the URL into Redis
            self.server.lpush(self.redis_key, next_page)

    def ParseHouse(self, idx, house_info):
        property_info = defaultdict(lambda: None)
        property_info['title'] = house_info['title']
        property_info['price'] = house_info['rent']
        property_info['address'] = house_info['address']['complete']
        property_info['published_by'] = house_info['role']
        property_info['area'] = house_info['ping']
        property_info['floor'] = house_info['floor']
        property_info['house_type'] = house_info['type_space_name']

        # url
        property_info['url'] = self.house_page[idx]
        property_info['img_url'] = self.house_imgUrls[idx]

        item = RentalItem()
        item['title'] = property_info['title']
        item['price'] = property_info['price']
        item['address'] = property_info['address']
        item['published_by'] = property_info['published_by']
        item['area'] = property_info['area']
        item['floor'] = property_info['floor']
        item['house_type'] = property_info['house_type']
        item['url'] = property_info['url']
        item['img_url'] = property_info['img_url']
        item['coming_from'] = self.name
        return item


if __name__ == '__main__':
    import sys
    sys.path.append(
        '/home/jeffbla/Project/RentHouseCrawler/RentHouseWebCrawler')

    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl(RentalSpider_ddroom)
    process.start()
