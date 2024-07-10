import scrapy
from scrapy_spider.items import Manual

class ExampleSpider(scrapy.Spider):
    name = "maytronics.com"
    start_urls = ['https://www.maytronics.com/robots.txt']

    def parse(self, response):
        for line in response.text.splitlines():
            if line.startswith('Sitemap:'):
                sitemap_url = line.split(': ', 1)[1]
                yield scrapy.Request(url=sitemap_url, callback=self.parse_xml)
                break

    def parse_xml(self, response):
        ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        first_link = response.xpath('//ns:sitemap[1]/ns:loc/text()', namespaces=ns).get()
        # Check if the first_link is not empty before yielding the result
        if first_link:
            yield scrapy.Request(url=first_link, callback=self.parse_next)

    def parse_next(self, response):
        urls = response.xpath("//ns:loc/text()", namespaces={"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}).extract()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_product_page)

    def parse_product_page(self, response):
        product_model = response.css('.product-name::text').get()
        product_url = response.css('meta[property="og:url"]::attr(content)').get()
        thumb = response.css('.overlay::attr(href)').get()
        breadcrumb_items = response.css('nav.breadcrumb li.breadcrumb-item a::text').getall()
        if len(breadcrumb_items) > 3:
            if breadcrumb_items[-1].strip() == "Best Seller Cleaners":
                product_name = "Robotic Pool Cleaners"
            else:
                product_name = breadcrumb_items[-1].strip()
            manual = Manual(
                model=product_model,
                brand='Maytronics',
                product= product_name,
                product_lang='en',
                type='Full Manual',
                url=product_url,
                thumbs=thumb,
                source=self.name
            )
        
        pdf_link = response.css('.manual-link::attr(href)').get()
        if pdf_link is not None and pdf_link != '':
            yield scrapy.Request(url=pdf_link, meta={'manual': manual}, callback=self.get_pdfs)

    def get_pdfs(self, response):
        product_manual = response.meta['manual']
        file_urls = response.css('a.ga-click::attr(href)').getall()
        # product_manual['type'] = response.css('button.btn.bg-black::text').get().strip()
        for url in file_urls:
            if url and url.endswith(".pdf") and url != "/images/pdfs/parts/caddy/CADDY_pro.pdf":
                product_manual['file_urls'] = url
                yield product_manual
