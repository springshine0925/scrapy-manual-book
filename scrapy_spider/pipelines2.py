import hashlib
import logging
import mimetypes

import swiftclient
from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FilesPipeline, FileException
from scrapy.utils.python import to_bytes
from io import BytesIO
from scrapy.utils.misc import md5sum
from scrapy.http import Request
import os
from swiftclient.exceptions import ClientException
import functools
from PIL import Image

logger = logging.getLogger(__name__)


class ManualScraperExtPipeline(FilesPipeline):
    SWIFT_CLIENT = None

    OS_authurl = None
    OS_user = None
    OS_key = None
    OS_tenant_name = None
    OS_auth_version = None
    OS_tenant_id = None
    OS_region_name = None

    def __init__(self, store_uri, download_func=None, settings=None):
        cls_name = "ManualScraperExtPipeline"
        resolve = functools.partial(self._key_for_pipe,
                                    base_class_name=cls_name,
                                    settings=settings)

        self.OS_authurl = settings.get(resolve('OS_authurl'), self.OS_authurl) or os.environ.get('OS_authurl')
        self.OS_user = settings.get(resolve('OS_user'), self.OS_user) or os.environ.get('OS_user')
        self.OS_key = settings.get(resolve('OS_key'), self.OS_key) or os.environ.get('OS_key')
        self.OS_tenant_name = settings.get(resolve('OS_tenant_name'), self.OS_tenant_name) or os.environ.get('OS_tenant_name')
        self.OS_auth_version = settings.get(resolve('OS_auth_version'), self.OS_auth_version) or os.environ.get('OS_auth_version')
        self.OS_tenant_id = settings.get(resolve('OS_tenant_id'), self.OS_tenant_id) or os.environ.get('OS_tenant_id')
        self.OS_region_name = settings.get(resolve('OS_region_name'), self.OS_region_name) or os.environ.get('OS_region_name')

        super(ManualScraperExtPipeline, self).__init__(store_uri, download_func=download_func, settings=settings)

    def open_spider(self, spider):
        super(ManualScraperExtPipeline, self).open_spider(spider)
        self.SWIFT_CLIENT = swiftclient.client.Connection(
            authurl=self.OS_authurl,
            user=self.OS_user,
            key=self.OS_key,
            tenant_name=self.OS_tenant_name,
            auth_version=self.OS_auth_version,
            os_options={
                'tenant_id': self.OS_tenant_id,
                'region_name': self.OS_region_name
            })

    def close_spider(self, spider):
        self.SWIFT_CLIENT.close()

    def get_media_requests(self, item, info):
        referer = item['url']
        meta = item.get('scrapfly') if item.get('scrapfly') else {}
        meta['SCRAPFLY_RENDER_JS'] = False
        files = item.get(self.files_urls_field, [])
        if not files:
            return []
        file = files[0] if isinstance(files, list) else files

        if isinstance(file, bytes):
            item[self.files_urls_field] = None
            if b'PDF' not in file[0:10]:
                raise DropItem("File is not a valid PDF")

            buf = BytesIO(file)
            path = '%s.pdf' % hashlib.sha1(file).hexdigest()
            checksum = md5sum(buf)
            buf.seek(0)

            self.os_store(path, buf)
            item['alt_files'] = [{'path': path, 'checksum': checksum, 'status': 'downloaded'}]

            return []
        else:
            # if (info.spider.settings.get('SCRAPFLY_ASP') or meta.get('SCRAPFLY_ASP')) and self.OS_authurl:
            if self.OS_authurl:
                path = self.path(file)
                exists = True
                obj = None
                try:
                    obj = self.SWIFT_CLIENT.head_object('scrapy', path)
                except ClientException as e:
                    if e.http_status == 404:
                        exists = False
                if exists:
                    item['alt_files'] = [{'path': path, 'status': 'already_exists', 'checksum': obj['etag']}]
                    return []

            return [Request(file, headers={'referer': referer}, meta=meta)]

    def file_path(self, request, response=None, info=None):
        return self.path(request.url)

    def path(self, url):
        if self.files_result_field == 'files':
            media_ext = '.pdf'
        else:
            media_ext = os.path.splitext(url)[1]
            # Handles empty and wild extensions by trying to guess the
            # mime type then extension or default to empty string otherwise
            if media_ext not in mimetypes.types_map:
                media_ext = ''
                media_type = mimetypes.guess_type(url)[0]
                if media_type:
                    media_ext = mimetypes.guess_extension(media_type)
        return hashlib.sha1(to_bytes(url)).hexdigest() + media_ext

    def file_downloaded(self, response, request, info):
        if b'PDF' not in response.body[0:20]:
            raise DropItem("Item contains no PDF: " + response.url)

        path = self.file_path(request, response=response, info=info)
        buf = BytesIO(response.body)
        checksum = md5sum(buf)
        buf.seek(0)

        self.os_store(path, buf)

        return checksum

    def os_store(self, path, buf):
        # only store in production to prevent errors
        if self.OS_authurl:
            self.SWIFT_CLIENT.put_object('scrapy', path, buf)



class ManualScraperImagePipeline(ManualScraperExtPipeline):
    DEFAULT_FILES_URLS_FIELD = 'thumb_urls'
    DEFAULT_FILES_RESULT_FIELD = 'thumbs'

    def __init__(self, store_uri, download_func=None, settings=None):
        super(ManualScraperImagePipeline, self).__init__(store_uri, download_func=download_func, settings=settings)
        self.files_urls_field = 'thumb_urls'
        self.files_result_field = 'thumbs'

    def file_downloaded(self, response, request, info):
        try:
            img = Image.open(BytesIO(response.body))
            if img.size[0] < 100 or img.size[1] < 100:
                logger.warning('Image size is less than 100 px: ' + response.url)
                info.spider.crawler.stats.inc_value('image/size_warning', spider=info.spider)
        except:
            info.spider.crawler.stats.inc_value('image/unknown_format', spider=info.spider)
            raise FileException('Image not readable: ' + response.url)

        info.spider.crawler.stats.inc_value('image/success', spider=info.spider)

        path = self.file_path(request, response=response, info=info)
        buf = BytesIO(response.body)
        checksum = md5sum(buf)
        buf.seek(0)

        self.os_store(path, buf)

        return checksum

    def get_media_requests(self, item, info):
        referer = item['url']
        meta = item.get('scrapfly') if item.get('scrapfly') else {}
        meta['SCRAPFLY_RENDER_JS'] = False
        files = item.get(self.files_urls_field, [])
        if not files:
            return []
        file = files[0] if isinstance(files, list) else files

        info.spider.crawler.stats.inc_value('image/start', spider=info.spider)

        headers = {}
        if info.spider.crawler.settings['CRAWLERA_ENABLED']:
            headers = {
                # removed AVIF as accepted image mime
                'X-Crawlera-Profile-Pass': 'Accept',
                'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'
            }

        return [
            Request(file, headers={
                'referer': referer,
                **headers
            }, meta=meta, dont_filter=True)
        ]

