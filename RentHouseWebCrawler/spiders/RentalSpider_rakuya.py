import re
import scrapy
import logging
from collections import defaultdict
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from scrapy_redis.spiders import RedisSpider

from RentHouseWebCrawler.items import RentalItem


class RentalSpider_rakuya(RedisSpider):
    name = 'rakuya'
    allowed_domains = ['rakuya.com.tw']  # Replace with the actual domain
    redis_key = f'{name}:start_urls'

    custom_settings = {
        # Close the spider after processing 1000 items. Since it has too many data.
        'CLOSESPIDER_ITEMCOUNT': 1000
    }

    def parse(self, response):
        # Extract house listings
        house_list = response.css('div.content.type-list.clearfix')
        # cover image
        house_imgStrs = house_list.css('a.obj-cover::attr(style)').getall()
        self.house_urls = house_list.css('a.obj-cover::attr(href)').getall()
        self.house_imgUrls = []
        for imgStr in house_imgStrs:
            imgStr = imgStr.split("'")[1]
            self.house_imgUrls.append(imgStr)

        # house info
        for self.house_page in self.house_urls:
            yield scrapy.Request(self.house_page, callback=self.ParseHouse)

        # next page
        # Follow pagination links
        num_pages = response.css('p.pages::text').get()
        num_pages = int(re.findall(r'\b\d+\b',
                                   num_pages)[-1])  # e.g. 第 1 / 209 頁
        for i in range(2, num_pages + 1):
            # Parse the URL
            url_parts = urlparse(response.url)
            query_params = parse_qs(url_parts.query)

            # Update the 'page' parameter
            query_params['page'] = [str(i)]

            # Reconstruct the URL with the updated query parameters
            new_query = urlencode(query_params, doseq=True)
            next_page = urlunparse(
                (url_parts.scheme, url_parts.netloc, url_parts.path,
                 url_parts.params, new_query, url_parts.fragment))
            self.logger.info(f'Next page: {next_page}')

            # push the URL into Redis
            self.server.lpush(self.redis_key, next_page)

    def ParseHouse(self, response):
        property_info = defaultdict(lambda: None)
        property_info['title'] = response.css('span.title::text').get()
        price = response.css('span.txt__price-total::text').get()
        property_info['price'] = int(price.replace(',', ''))
        property_info['address'] = response.css(
            'h1.txt__address::text')[1].get().strip()
        property_info['published_by'] = response.css('span.name::text').get()
        obj_infos = response.css('div.block__info-sub div.list__info-sub')
        for obj_info in obj_infos:
            conds = obj_info.css('span.list__label::text').getall()
            vals = obj_info.css('span.list__content::text').getall()
            if len(conds) == 0:
                if obj_info.css('h4.title-6::text').get() == '坪數':
                    if len(vals) != 0:
                        area = vals[0]
                        property_info['area'] = float(area.split('坪')[0])
            for idx, cond in enumerate(conds):
                if cond == '樓層/樓高':
                    property_info['floor'] = vals[idx]
                elif cond == '類型':
                    property_info['house_type'] = vals[idx]
                elif cond == '型態':
                    property_info['building_type'] = vals[idx]
                elif cond == '格局':
                    property_info['layout'] = vals[idx]
                elif cond == '短期租賃':
                    property_info['min_rent_period'] = vals[idx]
                elif cond == '性別要求':
                    property_info['gender_req'] = vals[idx]

            # facilities
            property_info['facilities'] = response.css('li.is--block b::text')

            # url
            property_info['url'] = self.house_page
            property_info['img_url'] = self.house_imgUrls[
                self.house_urls.index(self.house_page)]

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
        yield item


if __name__ == '__main__':
    import sys
    sys.path.append(
        '/home/jeffbla/Project/RentHouseCrawler/RentHouseWebCrawler')

    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl(RentalSpider_rakuya)
    process.start()
