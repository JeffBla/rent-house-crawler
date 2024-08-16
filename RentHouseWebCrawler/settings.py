BOT_NAME = 'RentHouseWebCrawler'

SPIDER_MODULES = ['RentHouseWebCrawler.spiders']
NEWSPIDER_MODULE = 'RentHouseWebCrawler.spiders'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

FEEDS = {
    'RentHouseInfo.json': {
        'format': 'json',
        'encoding': 'utf8',
        'indent': 4,
        'overwrite': True
    }
}

DOWNLOAD_DELAY = 2
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
CONCURRENT_REQUESTS_PER_DOMAIN = 8
CONCURRENT_REQUESTS = 16
RANDOMIZE_DOWNLOAD_DELAY = True

# LOG_LEVEL = 'INFO'
# LOG_FILE = 'log.log'
# LOG_FILE_APPEND = False
