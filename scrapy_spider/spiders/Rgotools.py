from scrapy.spiders import SitemapSpider
from scrapy_spider.items import Manual
import re

class BoompodsSpider(SitemapSpider):
    name = 'r-go-tools.com'
    sitemap_urls = ['https://www.r-go-tools.nl/product-sitemap1.xml']

    def parse(self, response, **cb_kwargs):
        for doc in response.css('a[href$=".pdf"]'):
            product = response.css('.posted_in a::text').get()
            model = response.css('h1.product_title.entry-title::text').re_first(r'(?i)(?:R-Go)?\s*(.+)')
            words = model.split()
            if len(words) >= 2:
                re_model = " ".join(words[:2])
            else:
                re_model = model
            doc_type = "Manual"
            language = response.css('::attr("lang")').get()[:2]
            gtin = response.css('p.variation-gtin::text').get()
            eans = re.search(r'\d+', gtin).group()
            
            yield Manual(
                model=re_model,
                brand='R-Go Tools',
                product=product,
                product_lang= 'en',
                file_urls=[doc.css('::attr("href")').get().strip()],
                type=doc_type,
                eans = eans,
                url=response.url,
                thumb_urls=response.css('img.wp-post-image.wvg-post-image.attachment-woocommerce_single.size-woocommerce_single ::attr("srcset")').get().split()[-2],
                source=self.name,
            )
