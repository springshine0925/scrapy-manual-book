# Scrapy settings for scrapy_spider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'manual_scraper_ext'
FEED_EXPORT_ENCODING = 'utf-8'

SPIDER_MODULES = ['manual_scraper_ext.spiders']
NEWSPIDER_MODULE = 'manual_scraper_ext.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'manual_scraper_ext (+http://www.yourdomain.com)'
# USER_AGENT='my-cool-project (http://example.com)'
# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
   "manual_scraper_ext.transformations.AbsoluteUrlMiddleware": 541,
   'manual_scraper_ext.middlewares.VideoMiddleware': 543,
   'manual_scraper_ext.middlewares.ItemEnrichment': 544,
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy_random_useragent_pro.middleware.RandomUserAgentMiddleware': 100,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,  # important
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy_crawlera.CrawleraMiddleware': 610,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    'manual_scraper_ext.middlewares.ScrapflyDownloaderMiddleware': 726,
    'manual_scraper_ext.middlewares.ProductDataMiddleware': 100,
    # 'manual_scraper_ext.middlewares.ManualScraperExtDownloaderMiddleware': 543,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "manual_scraper_ext.transformations.SchemaValidationPipeline": 150,
    "manual_scraper_ext.transformations.ResourceFilterPipeline": 200,
    'manual_scraper_ext.pipelines.ManualScraperExtPipeline': 300,
    'manual_scraper_ext.pipelines.ManualScraperImagePipeline': 301,
}

FILES_STORE = 'data'
FILES_URLS_FIELD = 'file_urls'
FILES_RESULT_FIELD = 'files'

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

OS_authurl = os.environ.get('OS_authurl')
OS_user = os.environ.get('OS_user')
OS_key = os.environ.get('OS_key')
OS_tenant_name = os.environ.get('OS_tenant_name')
OS_auth_version = os.environ.get('OS_auth_version')
OS_tenant_id = os.environ.get('OS_tenant_id')
OS_region_name = os.environ.get('OS_region_name')

SPLASH_URL = 'https://e0bwohoy-splash.scrapinghub.com'

RANDOM_UA_ENABLED = True

MEDIA_ALLOW_REDIRECTS = True

RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429, 403]  # added 403

SCRAPFLY_API_KEY = os.environ.get('SCRAPFLY_API_KEY') or 'scp-test-49fe37544bfb474486d714f5f068d6e6'
SCRAPFLY_ENABLED = False
SCRAPFLY_ASP = False
SCRAPFLY_RENDER_JS = False
SCRAPFLY_COUNTRY = False
SCRAPFLY_RENDERING_WAIT = 1000

CRAWLERA_ENABLED = False
# CRAWLERA_APIKEY = '13d7125cf0fe490d8e57ed9ad143140c'
# CRAWLERA_URL = 'http://api.zyte.com:8011'
CRAWLERA_APIKEY = 'c15a33a5eed4401ea33cd20b6ea1e597'
CRAWLERA_URL = 'http://proxy.crawlera.com:8011'
MEMDEBUG_ENABLED = False

GOOGLE_APIKEY = os.environ.get('GOOGLE_APIKEY')