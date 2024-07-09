# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from datetime import datetime
from urllib.parse import quote_plus
import base64
import extruct
import scrapy.http
import swiftclient
from hashlib import md5
import json
from scrapy import signals, responsetypes
from scrapy.responsetypes import responsetypes
from scrapy.http import TextResponse
import re

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

from manual_scraper_ext.helpers import store


class ManualScraperExtSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ManualScraperExtDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ScrapflyDownloaderMiddleware:

    def process_request(self, request, spider):

        # merge spider settings with possible overwrites from meta
        settings = {**spider.settings, **request.meta}

        if settings['SCRAPFLY_ENABLED'] and ('.pdf' not in request.url or request.meta.get('retry_times')):

            if request.meta.get("_scrapfly_processed"):
                # don't process the same request more than once
                # spider.logger.info('Don\'t process the same request more than once: %s' % request.url)
                return None

            request.meta['_scrapfly_processed'] = True

            key = settings['SCRAPFLY_API_KEY']
            request.meta['scrapfly_url'] = request.url
            url = quote_plus(request.url)
            wait_for_selector = quote_plus(str(request.meta.get('wait_for_selector') or 'false'))
            rendering_wait = str(settings['SCRAPFLY_RENDERING_WAIT'] or 1000)
            country = settings['SCRAPFLY_COUNTRY'] or ''
            render_js = 'true' if settings['SCRAPFLY_RENDER_JS'] else 'false'
            asp = 'true' if settings['SCRAPFLY_ASP'] else 'false'
            js = request.meta.get('js', None)
            js = base64.urlsafe_b64encode(js.encode('ascii')).decode('ascii') if js else ''
            js_scenario = request.meta.get('js_scenario', None)
            js_scenario = base64.urlsafe_b64encode(json.dumps(js_scenario).encode('ascii')).decode('ascii') if js_scenario else ''
            proxy_url = f"https://api.scrapfly.io/scrape" \
                        f"?key={key}" \
                        f"&waitForSelector={wait_for_selector}" \
                        f"&rendering_wait={rendering_wait}" \
                        f"&country={country}" \
                        f"&asp={asp}" \
                        f"&render_js={render_js}" \
                        f"&js={js}" \
                        f"&js_scenario={js_scenario}" \
                        f"&headers[cookie]={quote_plus(request.meta.get('SCRAPFLY_COOKIES', ''))}" \
                        f"&url={quote_plus(url)}"
            spider.logger.info('Scrapfly request: %s' % request.url)
            request.meta['download_slot'] = '__splash__'
            new_request = request.replace(url=proxy_url)
            return new_request
        else:
            return None

    def process_response(self, request, response, spider):
        if not request.meta.get("_scrapfly_processed"):
            return response

        if not request.meta.get('scrapfly_url'):
            return response

        try:
            obj = json.loads(response.body)
        except:
            spider.logger.error('Json error for url %s' % response.url)
            spider.logger.error('Value: %s' % response.text)
            return response

        if 'x-scrapfly-api-cost' in response.headers:
            spider.crawler.stats.inc_value('scrapfly/api_call_cost', count=int(response.headers['x-scrapfly-api-cost']))

        if obj['result']['format'] == 'binary':
            obj['result']['content'] = base64.b64decode(obj['result']['content'])

        spider.logger.debug('Log url: %s' % obj['result']['log_url'])

        obj['result']['response_headers']['Content-Encoding'] = None

        response = response.replace(
            body=obj['result']['content'],
            headers=obj['result']['response_headers'],
            url=obj['result']['url'],
            status=obj['result']['status_code'] or 200,
            request=request.replace(meta={
                **request.meta,
                'browser_data': obj['result']['browser_data']
            }),
        )
        respcls = responsetypes.from_args(headers=response.headers, url=response.url, body=response.body)

        from scrapy.http.response import Response
        if isinstance(response, TextResponse) and respcls is Response:
            return response
        return response.replace(cls=respcls)


class ProductDataMiddleware:
    def process_response(self, request, response, spider):
        if b'<html' not in response.body:
            return response
        try:
            data = extruct.extract(
                response.body,
                syntaxes=['microdata', 'json-ld'],
                base_url=response.urljoin('/'),
                uniform=True,
            )
            swift = swiftclient.client.Connection(
                authurl=spider.settings['OS_authurl'],
                user=spider.settings['OS_user'],
                key=spider.settings['OS_key'],
                tenant_name=spider.settings['OS_tenant_name'],
                auth_version=spider.settings['OS_auth_version'],
                os_options={
                    'tenant_id': spider.settings['OS_tenant_id'],
                    'region_name': spider.settings['OS_region_name']
                })

            data['microdata'] = self.sanitize(data['microdata'])
            data['json-ld'] = self.sanitize(data['json-ld'])
            data['lang'] = response.css('html::attr("lang")').get()
            data['created_at'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S%z')
            data['url'] = response.url

            if len(data['microdata']) or len(data['json-ld']):
                content = json.dumps(data, indent=4, sort_keys=True)
                url = spider.name + '/' + md5(response.url.encode()).hexdigest() + '.json'
                swift.put_object('scrapy_productdata', url, content)
        except Exception as e:
            return response

        return response

    def sanitize(self, obj):
        if len(list(filter(lambda i: '@type' in i and i['@type'] in ['Product'], obj))):
            return list(
                filter(lambda i: '@type' in i and i['@type'] in ['BreadcrumbList', 'Product', 'Website', 'Brand'], obj)
            )
        return []


class VideoMiddleware:
    def process_spider_output(self, response, result, spider):
        for x in result:
            if isinstance(x, scrapy.Item) and hasattr(response, 'text'):
                youtube = re.findall(r"(?:youtube\.com\/(?:(?:vi?|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})", response.text, re.IGNORECASE)
                mp4 = list(map(lambda url: response.urljoin(url), re.findall(r"\"([^\"]*\.mp4)\"", response.text, re.IGNORECASE)))
                if youtube or mp4:
                    x['video'] = {
                        'youtube': youtube,
                        'mp4': mp4,
                    }
            yield x


class ItemEnrichment:
    def process_spider_output(self, response, result, spider):
        for x in result:
            if isinstance(x, scrapy.Item) and hasattr(response, 'text'):
                if 'eans' not in x or not x['eans']:
                    x['eans'] = response.css('script::text').re_first(r'\"gtin13\":\s?\"(\d{13})\"')

            yield x
