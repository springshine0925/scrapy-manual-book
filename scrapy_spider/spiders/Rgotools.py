from scrapy.spiders import SitemapSpider
from scrapy_spider.items import Manual
import re

class BoompodsSpider(SitemapSpider):
    name = 'r-go-tools.com'
    sitemap_urls = ['https://www.r-go-tools.nl/product-sitemap1.xml']

    def parse(self, response, **cb_kwargs):
        # yield{'url': response.url}

        for doc in response.css('ul.links li.download:first-child a[href$=".pdf"]'):
            manual_link = response.css('ul.links li.download:first-child a')
            manual_text = manual_link.css('::text').get()
            manual_url = manual_link.css('::attr(href)').get()
            if "Handleiding" in manual_text and manual_url:
                product = response.css('.posted_in a::text').get()
                model = response.css('h1.product_title.entry-title::text').re_first(r'(?i)(?:R-Go)?\s*(.+)')
                words = model.split()
                if len(words) >= 2:
                    re_model = " ".join(words[:2])
                else:
                    re_model = model
                # print(re_model)
                doc_type = "Manual"
                language = response.css('::attr("lang")').get()[:2]
                gtin = response.css('p.variation-gtin::text').get()
                eans = re.search(r'\d+', gtin).group()
                pdf_url= doc.css('a::attr("href")').get().strip()
                yield Manual(
                    model=re_model,
                    brand='R-Go Tools',
                    product=product,
                    product_lang= 'en',
                    file_urls=[pdf_url],
                    type=doc_type,
                    eans = eans,
                    url=response.url,
                    thumb_urls=response.css('img.wp-post-image.wvg-post-image.attachment-woocommerce_single.size-woocommerce_single ::attr("srcset")').get().split()[-2],
                    source=self.name,
                )
