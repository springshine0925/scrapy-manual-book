import scrapy
from scrapy.http import Request
from scrapy_spider.items import Manual

class IvankyoSpider(scrapy.Spider):
    name = "ivankyo1.com"
    allowed_domains = ["ivankyo.com"]
    start_urls = ["https://ivankyo.com/collections/mini-projector"]

    def parse(self, response):
        product_cards = response.css('.products')  # Select individual product cards
        product = product_cards.xpath('.//div')
        if response.url == "https://ivankyo.com/collections/sewing-projectors":
            product_cards = response.css('.section8Container')
            product = product_cards.css('.productListItem')

        for card in product:
            # print(card.allget())
            # for block in card:
            relative_url = card.css('a::attr(href)').extract_first()  # Extract the relative URL from the href attribute
            if response.url == "https://ivankyo.com/collections/sewing-projectors":
                relative_url = card.xpath('.//div.productImgBlock//a::href')
            absolute_url = response.urljoin(relative_url)  # Convert the relative URL to absolute URL
                
            yield scrapy.Request(absolute_url, meta={'relative_url': relative_url}, callback=self.parse_detail)

    def parse_detail(self, response):
        product_model = response.css('.product_name::text').get()
        product_url = response.meta.get('relative_url', '')
        thumb = response.css('li img::attr(src)').extract_first()
        breadcrumb_elements = response.css('.breadcrumb--text a::text').extract()
        product_parent = breadcrumb_elements[-2].strip() if len(breadcrumb_elements) >= 2 else ''
        product_name = breadcrumb_elements[-1].strip() if breadcrumb_elements else ''
        if product_name != 'all':

            manual = Manual(
                model=product_model,
                brand='ivankyo',
                product=product_name,
                product_parent= '',
                product_lang='en',
                file_urls='',  # Initialize as an empty list
                type='User Manual',
                url=product_url,
                thumbs=thumb,
                source=self.name
            )

            pdf_url = response.css('h5 a::attr(href)').get()
            manual['file_urls'] = [ pdf_url] # Set the file URLs in the manual item
            
            yield manual
