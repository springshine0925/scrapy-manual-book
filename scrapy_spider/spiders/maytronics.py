import scrapy
from scrapy.http import Request
from scrapy_spider.items import Manual
import time

class ExampleSpider(scrapy.Spider):
    name = "maytronics.com1"
    allowed_domains = ["maytronics.com"]
    start_urls = ["https://www.maytronics.com/global/store/"]
   
    def parse(self, response):

        while response.css('button.more'):  # Check if the button is still present and clickable
            button = response.css('button.more')
            data_url = button.css('::attr(data-url)').get()
            if not data_url:
                break  # Exit the loop if data-url attribute is not found

            response = response.follow(url=data_url)
            yield scrapy.Request(url=data_url, callback=self.parse_btn)

        yield scrapy.Request(url=self.start_urls, callback=self.parse_next_page)
    def parse_next_page(self, response):
        product_cards = response.css('.product')  # Select individual product cards

        for card in product_cards:
            relative_url = card.css('a.product-learn-more::attr(href)').get()  # Extract the relative URL from the href attribute
            absolute_url = response.urljoin(relative_url)  # Convert the relative URL to absolute URL
            yield scrapy.Request(absolute_url, callback=self.parse_detail)

    def parse_detail(self, response):
        product_model = response.css('.product-name::text').get()
        product_url = response.css('meta[property="og:url"]::attr(content)').get()
        thumb = response.css('.overlay::attr(href)').get()
        breadcrumb_items = response.css('nav.breadcrumb li.breadcrumb-item a::text').getall()
        manual = Manual(
            model=product_model,
            brand='maytronics',
            product=breadcrumb_items[-1],
            product_parent=breadcrumb_items[-2],
            product_lang='en',
            file_urls='',  # Placeholder for the file URLs
            type='',
            url=product_url,
            thumbs=thumb,
            source= self.name
        )

        # Extract the PDF link and yield a request to get the PDFs
        pdf_url = response.css('.manual-link::attr(href)').get()
        yield Request(url=pdf_url, meta={'manual': manual}, callback=self.get_pdfs)

    def get_pdfs(self, response):
        pdf_link = response.css('a[data-button-language="English"].ga-click::attr(href)').get()
        manual = response.meta['manual']
        manual['file_urls'] = pdf_link  # Set the file URLs in the manual item
        manual['type'] = response.css('button.btn.bg-black::text').get().strip()

        yield manual
