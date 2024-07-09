from scrapy.spiders import SitemapSpider
from scrapy_spider.items import Manual


class BoompodsSpider(SitemapSpider):
    name = 'boompods.com'
    sitemap_urls = ['https://de.boompods.com/wp-sitemap-posts-product-1.xml']

    def parse(self, response, **cb_kwargs):
        for doc in response.css('a[href$=".pdf"]'):

            product = response.css('.posted_in a::text').get()
            model = ' '.join(' '.join(response.xpath('//h1//text()').extract()[:-1]).split())
            if 'Archive' in product:
                if 'pod' in model:
                    product = 'Speakers'
                elif 'buds' in model:
                    product = 'Headphones'
                elif 'solar power bank' in model or 'POWER' in model:
                    model = model.replace('solar power bank', '').strip()
                    product = 'Power bank'
                elif 'case' in model:
                    product = 'Power case'
                elif 'earphones' in model or 'Bassline' in model:
                    product = 'Earphones'
                    model = model.replace('earphones', '').strip()
                else:
                    product = 'Speaker'
            doc_type = doc.css('::text').get().split()[-1]
            if 'Benutzerhandbuch' in doc_type:
                doc_type = 'Benutzerhandbuch'
            yield Manual(
                model=model,
                brand='Boompods',
                product=product,
                product_lang=response.css('::attr("lang")').get()[:2],
                file_urls=[doc.css('::attr("href")').get().strip()],
                type=doc_type.title(),
                url=response.url,
                thumb_urls=response.css('img.no-sirv-lazy-load::attr("srcset")').get().split()[-2],
                source=self.name,
            )
