import scrapy
from scrapy_spider.items import Manual

class RMEAudioSpider(scrapy.Spider):
    name = "rme-audio.de"
    allowed_domains = ["rme-audio.de", "docs.rme-audio.com"]
    start_urls = ["https://rme-audio.de/downloads.html"]
    user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
    handle_httpstatus_list = [301, 302]

    custom_settings = {
        # 'CONCURRENT_REQUESTS': 2,
        # 'DOWNLOAD_DELAY': 0.2,
        'ROBOTSTXT_OBEY': False,
        'DUPEFILTER_DEBUG': True,  # Set this to True to debug duplicate filtering
    }

    category_mapping = {
        'PCI & Cardbus': 'mic_preamps',
        'Firewire & USB': 'firewire_usb',
        'MADI & AES': 'madi_aes',
        'Audio-Converter / Format-Converter': 'audio_converter_format_converter',
        'Mic Preamps': 'mic_preamps',
        'Accessories': 'accessories'
    }

    def parse(self, response):
        li_tags = response.css('ul.categories li')
        brand = 'RME'

        for li in li_tags:
            category_text = li.css('::text').get().strip()
            converted_category = self.category_mapping.get(category_text, 
                category_text.lower().replace(' & ', '_').replace(' ', '_'))

            div_tags = response.xpath(f'//div[@data-category="{converted_category}"]/div')

            for div in div_tags:
                product_name = div.css('div.manual-title::text').get().strip()
                pdf_url = div.css('div.manual-download a::attr(href)').get()
                manual = Manual()
                
                manual['model'] = product_name
                manual['brand'] = brand
                manual['product'] = category_text
                manual['product_lang'] = 'en'
                manual['type'] = 'Manual'
                manual['url'] = response.url
                manual['source'] = self.name

                if pdf_url and pdf_url.endswith(".pdf"):
                    manual['file_urls'] = [response.urljoin(pdf_url)]
                    yield manual
                elif pdf_url:
                    yield{
                        'pdf_url': pdf_url,
                        'product_name': product_name
                    }
                    yield scrapy.Request(url=f'{pdf_url}/shared', meta={'manual': manual}, callback=self.parse_url)

    def parse_url(self, response):
        yield{
            'get_url': response.url
        }
        product_manual = response.meta['manual']
        product_model = product_manual['model']

        if product_model == "M-32 Pro AD" or product_model == "M-32 Pro DA":
            items = product_model.split()
            re_model_names = [items[0], items[2], items[1]]
            product_model = ''.join(re_model_names)

        products = response.xpath('//table/tbody/tr')
        
        for product in products:
            product_name = product.xpath('td[1]/p/text()').get()
            new_product_name = product_name.replace("RME", "").strip()
            relative_pdf_url = product.xpath('td[3]/p/a/@href').get()
            if relative_pdf_url:
                pdf_url_correct = response.urljoin(relative_pdf_url)
                if self.compare(new_product_name, product_model) and pdf_url_correct.endswith(".pdf"):
                    product_manual['file_urls'] = [pdf_url_correct]
                    product_manual['url'] = response.url
                    yield product_manual
                    break
            else:
                yield {
                    "product": new_product_name,
                    'model': product_model
                }

    def compare(self, product, model):
        return product.lower() == model.lower()