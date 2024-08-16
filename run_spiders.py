from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from RentHouseWebCrawler.spiders import RentalSpider_ddroom, RentalSpider_rakuya

if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())

    # Add each spider you want to run
    process.crawl(RentalSpider_ddroom.RentalSpider_ddroom)
    process.crawl(RentalSpider_rakuya.RentalSpider_rakuya)

    # Start the crawling process
    process.start(
    )  # The script will block here until all crawling jobs are finished
