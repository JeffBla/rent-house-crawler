import scrapy
import logging
from collections import defaultdict
from RentHouseWebCrawler.items import RentalItem


class RentalSpider_ddroom(scrapy.Spider):
    name = 'ddroom'
    allowed_domains = ['api.dd-room.com',
                       'dd-room.com']  # Replace with the actual domain
    start_urls = [
        'https://api.dd-room.com/api/v1/search?category=house&order=recommend&sort=desc&page=1'
    ]  # Starting URL
    logger = logging.getLogger(name)
    logger.info(f'Domain: {allowed_domains}')
    logger.info(f'Starting URL: {start_urls}')

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
            yield scrapy.Request(next_page, self.parse)

    def ParseHouse(self, idx, house_info):
        property_info = defaultdict(lambda: None)
        property_info['title'] = house_info['title']
        property_info['price'] = house_info['rent']
        property_info['address'] = house_info['address']['complete']
        property_info['published_by'] = house_info['role']
        property_info['area'] = house_info['ping']
        property_info['floor'] = str(house_info['floor'])
        property_info['house_type'] = house_info['type_space_name']
        # property_info['building_type'] = house_info['category']
        # property_info['layout'] = list(map(lambda x: x['layout'], house_list))
        # property_info['min_rent_period'] = vals[idx]
        # property_info['gender_req'] = vals[idx]

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
        item['building_type'] = property_info['building_type']
        item['layout'] = property_info['layout']
        item['min_rent_period'] = property_info['min_rent_period']
        item['gender_req'] = property_info['gender_req']
        # item['facilities'] = property_info['facilities']
        item['url'] = property_info['url']
        item['img_url'] = property_info['img_url']
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
