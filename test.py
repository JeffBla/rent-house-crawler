import scrapy
import logging


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

    custom_settings = {
        'USER_AGENT':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    def parse(self, response):
        # Extract house listings
        house_list = response.css('div.content  type-list  clearfix')
        # cover image
        house_imgStrs = house_list.css('a.obj-cover::attr(style)').getall()
        house_urls = house_list.css('a.obj-cover::attr(href)').getall()
        house_imgUrls = []
        for imgStr in house_imgStrs:
            imgStr = imgStr.split("'")[1]
            house_imgUrls.append(imgStr)
        self.logger.info(f'house_imgUrls: {house_imgUrls}')
        # house info
        for house_page in house_urls:
            yield scrapy.Request(house_page, callback=self.ParseHouse)

        for listing in listings:
            yield {
                'title': listing.css('h2.title::text').get(),
                'price': listing.css('span.price::text').get(),
                'location': listing.css('span.location::text').get(),
                'bedrooms': listing.css('span.bedrooms::text').get(),
                'bathrooms': listing.css('span.bathrooms::text').get(),
                'link': response.urljoin(listing.css('a::attr(href)').get()),
            }

        # Follow pagination links
        next_page = response.css(
            'a.next-page::attr(href)').get()  # Adjust selector

        if next_page:
            yield response.follow(next_page, self.parse)

    def ParseHouse(self, response):
        title = response.css('span.title::text').get()
        price = response.css('span.price::text').get()
        address = response.css('h1.txt__address a::text')
        published_by = response.css('span.name::text').get()
        obj_infos = response.css('div.block__info-sub div.list__info-sub')
        for obj_info in obj_infos:
            cond = obj_info.css('span.list__label::text').get()
            val = obj_info.css('span.list__content::text').get()
            if cond == '':
                area = val
            elif cond == '樓層':
                floor = val
            elif cond == '型態':
                house_type = val
            elif cond == '建物型態':
                building_type = val
            elif cond == '格局':
                layout = val
            elif cond == '最短租期':
                min_rent_period = val
            elif cond == '性別要求':
                gender_req = val

            # facilities
            facilities = response.css('li.is--block b::text')
