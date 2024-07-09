import scrapy
from scrapy_spider.items import Manual

class RMEAudioSpider(scrapy.Spider):
    name = "rme-audio.de1"
    allowed_domains = ["rme-audio.de1"]
    start_urls = ["https://rme-audio.de/downloads.html"]

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
        
        for li in li_tags:
            category_text = li.css('::text').get().strip()
            converted_category = self.category_mapping.get(category_text, category_text.lower().replace(' & ', '_').replace(' ', '_'))
            div_tags = response.xpath(f'//div[@data-category="{converted_category}"]/div')

            for div in div_tags:
                product_name = div.css('div.manual-title::text').get().strip()
                pdf_url = div.css('div.manual-download a::attr(href)').get()

                manual = Manual(
                    model=product_name,
                    brand='RME',
                    product=category_text,
                    product_lang='de',
                    type='Manual',
                    url=response.url,
                    source=self.name
                )

                if ".pdf" in pdf_url:
                    manual['file_urls'] = [pdf_url] if pdf_url else []
                    yield manual
                else:
                    yield scrapy.Request(url=pdf_url, meta={'manual': manual}, callback=self.parse_pdf)

    def parse_pdf(self, response):
        product_manual = response.meta['manual']
        products = response.css('table.tableblock tbody tr')
        
        for product in products:
            product_name = product.css('td:nth-child(1) p::text').get()
            pdf_url = ""
            
            if product_name == product_manual['model']:
                pdf_url = product.css('td:nth-child(3) a::attr(href)').get()
                break  # Stop searching further once the target product is found
        if pdf_url:
            product_manual['file_urls']=pdf_url

            yield product_manual