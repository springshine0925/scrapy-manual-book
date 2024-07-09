import scrapy
from scrapy.http import Request
from scrapy_spider.items import Manual

class IvankyoSpider(scrapy.Spider):
    name = "ivankyo.com1"
    allowed_domains = ["ivankyo.com"]
    start_urls = [
        "https://ivankyo.com/collections/home-theater-projector",
        "https://ivankyo.com/collections/mini-projector",
        "https://ivankyo.com/collections/gaming-projector",
        "https://ivankyo.com/collections/outdoor-projector",
        "https://ivankyo.com/collections/projector-accessories",
        "https://ivankyo.com/collections/tablet"
        "https://ivankyo.com/collections/sewing-projectors",
    ]

    def parse(self, response):
        if "sewing-projectors" in response.url:
            product_cards = response.css('.section8Container .productListItem')
        else:
            product_cards = response.css('.products div')

        for card in product_cards:
            relative_url = card.css('a::attr(href)').extract_first()
            absolute_url = response.urljoin(relative_url)

            yield scrapy.Request(absolute_url, meta={'relative_url': relative_url}, callback=self.parse_detail)

    def parse_detail(self, response):
        product_model = response.css('.product_name::text').get()
        words = product_model.split()
        model = ' '.join(words[1:3]) if len(words) >= 3 else words[1]
        base_url = "https://ivankyo.com"
        relative_url = response.meta.get('relative_url', '')
        # product_url = f"{base_url}{relative_url}"
        product_url = "https://ivankyo.com/pages/download#Projector"
        thumb = response.css('li img::attr(src)').extract_first()
        breadcrumb_elements = response.css('.breadcrumb--text a::text').extract()
        product_name = breadcrumb_elements[-1].strip() if breadcrumb_elements else ''

        if product_name and product_name != 'all':
            manual = Manual(
                model=model,
                brand='VANKYO',
                product=product_name,
                product_parent= "",
                product_lang='en',
                file_urls=[],
                type='User Manual',
                url=product_url,
                thumbs=thumb,
                source=self.name
            )

            pdf_url = response.css('h5 a::attr(href)').get()

            if pdf_url is not None:
                manual['file_urls'] = [pdf_url] # Set the file URLs in the manual item
                
                yield manual
