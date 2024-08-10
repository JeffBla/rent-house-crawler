import re
import scrapy
import logging
from collections import defaultdict


class RentalSpider(scrapy.Spider):
    name = 'rental'
    allowed_domains = ['rakuya.com.tw']  # Replace with the actual domain
    start_urls = [
        f'https://www.rakuya.com.tw/rent/rent_search?search=city&city={cnt}&upd=1'
        for cnt in range(21)
    ]  # Starting URL
    logger = logging.getLogger(name)
    logger.info(f'Domain: {allowed_domains}')
    logger.info(f'Starting URL: {start_urls}')

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

        self.logger.info(f'house_imgUrls: {self.house_imgUrls}')
        # house info
        for self.house_page in self.house_urls:
            yield scrapy.Request(self.house_page, callback=self.ParseHouse)

        # next page
        # Follow pagination links
        num_pages = response.css('p.pages::text').get()
        num_pages = int(re.findall(r'\b\d+\b',
                                   num_pages)[-1])  # e.g. 第 1 / 209 頁
        for i in range(2, num_pages + 1):
            next_page = response.urljoin(f'&page={i}')
            yield scrapy.Request(next_page, self.parse)

    def ParseHouse(self, response):
        property_info = defaultdict(lambda: None)
        property_info['title'] = response.css('span.title::text').get()
        property_info['price'] = response.css('span.price::text').get()
        property_info['address'] = response.css('h1.txt__address a::text')
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
                elif cond == '型態':
                    property_info['house_type'] = vals[idx]
                elif cond == '類型':
                    property_info['building_type'] = vals[idx]
                elif cond == '格局':
                    property_info['layout'] = vals[idx]
                elif cond == '最短租期':
                    property_info['min_rent_period'] = vals[idx]
                elif cond == '性別要求':
                    property_info['gender_req'] = vals[idx]

            # facilities
            property_info['facilities'] = response.css('li.is--block b::text')

            # url
            property_info['url'] = self.house_page
            property_info['img_url'] = self.house_imgUrls[
                self.house_urls.index(self.house_page)]

        yield {
            'title': property_info['title'],
            'price': property_info['price'],
            'address': property_info['address'],
            'published_by': property_info['published_by'],
            'area': property_info['area'],
            'floor': property_info['floor'],
            'house_type': property_info['house_type'],
            'building_type': property_info['building_type'],
            'layout': property_info['layout'],
            'min_rent_period': property_info['min_rent_period'],
            'gender_req': property_info['gender_req'],
            # 'facilities': property_info['facilities'], # error due to it can't be serialized
            'url': property_info['url'],
            'img_url': property_info['img_url']
        }


if __name__ == '__main__':
    import sys
    sys.path.append(
        '/home/jeffbla/Project/RentHouseCrawler/RentHouseWebCrawler')

    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl(RentalSpider)
    process.start()
