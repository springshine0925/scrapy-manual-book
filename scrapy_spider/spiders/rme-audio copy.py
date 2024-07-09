import scrapy
from scrapy_spider.items import Manual

class RMEAudioSpider(scrapy.Spider):
    name = "rme-audio.de11"
    allowed_domains = ["rme-audio.de",'docs.rme-audio.com']
    start_urls = ["https://rme-audio.de/downloads.html"]
    custom_settings = {
        'CRAWLERA_ENABLED': True
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
        brand='RME'
        for li in li_tags:
            category_text = li.css('::text').get().strip()
            converted_category = self.category_mapping.get(category_text, category_text.lower().replace(' & ', '_').replace(' ', '_'))
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
                    manual['file_urls'] = pdf_url
                    # yield manual
                elif pdf_url:
                    yield scrapy.Request(url=f'{pdf_url}shared/', meta= {'manual': manual}, callback=self.parse_btn)
                                    

    def parse_btn(self, response):
        product_manual = response.meta['manual']
        product_manual['url'] = response.url
        products = response.css('table.tableblock tbody tr')
        product_model =  product_manual['model']
        if product_model =="M-32 Pro AD" or product_model == "M-32 Pro DA":
            items=product_model.split()
            re_model_names = [items[0], items[2], items[1]]
            product_model = ''.join(re_model_names)
        for product in products:
            product_name = product.css('td:nth-child(1) p::text').get()
            pdf_url = product.css('td:nth-child(3) a::attr(href)').get()

            if  product_name == product_model and pdf_url:
                product_manual['file_urls'] = pdf_url
                product_manual['url'] = response.url
                yield product_manual
                break

  
