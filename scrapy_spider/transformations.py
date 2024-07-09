import re
from os.path import splitext

from scrapy import Request, Item
from scrapy.linkextractors import IGNORED_EXTENSIONS
from scrapy.exceptions import DropItem

from manual_scraper_ext.items import ManualLoader

EXTS = set(IGNORED_EXTENSIONS)
EXTS.update(
    {
        "avi",
        "wmv",
        "mov",
        "flv",
        "3gp",
        "webp",
        "jpeg",
        "rtf",
        "webm",
        "msi",
        "ps",
        "f4v",
        "png",
        "gif",
        "flac",
        "vorb",
        "mpg",
        "bmp",
        "csv",
        "mp3",
        "aac",
        "m3u",
        "docx",
        "mp4",
        "tsv",
        "wav",
        "tiff",
        "aeif",
        "ogg",
        "txt",
        "xls",
        "raw",
        "heic",
        "avchd",
        "xlsx",
        "mkv",
        "wma",
        "eps",
        "aif",
        "jpg",
        "zip",
    }
)
EXTS.remove("pdf")
# print('IGNORE EXTs::> ', EXTS)


class ResourceFilterPipeline(object):
    """filter item with non pdf media"""

    IGNORE_NON_DOC_URL = re.compile(r"\." + r"|\.".join(EXTS), flags=re.I)

    def is_not_pdf(self, rsrc_path):
        ext = splitext(rsrc_path)[1]
        if bool(
            self.IGNORE_NON_DOC_URL.search(rsrc_path)
        ):
            return ext, bool(
                self.IGNORE_NON_DOC_URL.search(ext)
            )
        return ext, False

    def process_item(self, item, spider):
        if rsrc := item.get("file_urls"):
            rsrc_url = rsrc[0] if isinstance(rsrc, list) else rsrc
            rsrc_url = rsrc_url.split('/')[-1]
            # url is of .ext
            try:
                ext, is_invalid = self.is_not_pdf(rsrc_url)
                if is_invalid:
                    spider.crawler.stats.inc_value("other_ext_item")
                    raise DropItem(f"Item is a {ext}: {rsrc_url}")
            except:
                pass

        return item


class SchemaValidationPipeline(object):
    """filter item with null fields, guess certain fields"""

    REQ_FIELDS = {
        "brand",
        "model",
        # "type"
    }
    TEMP_IMG_FLAG = {"placeholder", "no-image", "product-default", "not-found", "missing", "noImg"}

    def process_item(self, item, spider):
        product_url = item.get("url")
        if self._none_validator(item, spider.crawler.stats):
            raise DropItem(
                f"Item doesn't contain required fields for {product_url}"
            )

        if not item.get("source"):
            item.update({"source": spider.name.lower()})
        if not item.get("product"):
            item.update({"product": "No Category"})

        if img := item.get("thumb_urls"):
            img = img.lower()
            if any(
                flag in img or flag.replace('-', '_') in img  
                for flag in self.TEMP_IMG_FLAG
            ):
                item.pop("thumb_urls", None)
                spider.log(f"Popped placeholder thumb for {product_url}")
                spider.crawler.stats.inc_value(
                    "placeholder_thumb_count", spider=spider
                )

        return ManualLoader(item=item).load_item()

    def _none_validator(self, item, stats):
        for req_field in self.REQ_FIELDS:
            if not item.get(req_field):
                stats.inc_value(f"filtered/null/{req_field}")
                return True
        return False


class AbsoluteUrlMiddleware:
    """convert relative url to absolute"""

    URL_FIELDS = {"url", "file_urls", "thumb_urls"}

    def process_spider_output(self, response, result, spider):
        return (
            r
            for r in result or ()
            if self._filter(r, response.urljoin, spider)
        )

    def _update_url_fields(self, result, _urljoin, spider):
        for field in self.URL_FIELDS:
            if val := result.get(field):
                _url = val[0] if isinstance(val, list) else val
                _url = _url.strip()
                if not _url.startswith("http"):
                    result.update({field: _urljoin(_url)})
                    spider.crawler.stats.inc_value(
                        f"relative_updation/{field}", spider=spider
                    )

    def _filter(self, request, _urljoin, spider):
        if isinstance(request, Item):
            if not any(request.get("file_urls") or request.get("alt_files") or []):
                spider.crawler.stats.inc_value(
                    "filtered/null/file_urls", spider=spider
                )
                return False

            self._update_url_fields(request, _urljoin, spider)

        return True
