# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Manual(scrapy.Item):
    model = scrapy.Field()  # product name without brand
    model_2 = scrapy.Field()  # alternative product name (optional)
    brand = scrapy.Field()  # brand name
    product = scrapy.Field()  # product (for example "washing machines")
    product_parent = scrapy.Field()  # "domestic appliances" for example (optional)
    product_lang = scrapy.Field()  # product field language, two digit language code (optional)
    file_urls = scrapy.Field()  # url to PDF (as an array)
    alt_files = scrapy.Field()  # only used for files without url
    eans = scrapy.Field()  # optional product EANs
    files = scrapy.Field()  # internal
    type = scrapy.Field()  # type, for example "quick start guide", "datasheet" or "manual" (optional if type = manual)
    url = scrapy.Field()  # url of the page containing link to pdf
    # thumb = scrapy.Field()  # replaced by thumb_urls
    thumbs = scrapy.Field()  # internal
    thumb_urls = scrapy.Field()  # thumbnail url (optional)
    video = scrapy.Field()  # video (optional)
    source = scrapy.Field()  # hostname without http/www to identify the source, for example dyson.com or walmart.com
    scrapfly = scrapy.Field()  # enable Scrapfly for download


from itemloaders.processors import TakeFirst, Identity
from scrapy.loader import ItemLoader


class ManualLoader(ItemLoader):

    default_output_processor = TakeFirst()
    identity_fields = {"files", "alt_files", "file_urls"}
    for _field in identity_fields:
        exec(f"{_field}_out = Identity()")
