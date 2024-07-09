import scrapy
import json
from scrapy_spider.items import Manual

class IvankyoSpider(scrapy.Spider):
    name = "ivankyo.com"
    allowed_domains = ["ivankyo.com"]
    start_urls = ["https://ivankyo.com/pages/download#all"]

    def parse(self, response):
        base_url = 'https://admin.ivankyo.com/index.php?route=api/product_downloads/getProductdownloads'

        yield scrapy.Request(url=base_url, callback=self.parse_detail)

    def parse_detail(self, response):
        data = json.loads(response.body)
        brand='VANKYO'
        for category, items in data.items():
            suburl = '%20'.join(category.split())
            for item in items:
                model_list = self.clean_model_name(item['title'])
                for model in model_list:
                    url_list = json.loads(item['url_list'])
                    if isinstance(url_list, dict):
                        for version, urls in url_list.items():
                            language = urls[0]['language']
                            url = urls[0]['url']
                            manual = Manual()
                            manual['model'] = model
                            manual['brand'] = brand
                            manual['product'] = category
                            manual['product_lang'] = 'en'
                            manual['file_urls'] = [url]
                            manual['type'] = 'User Manual'
                            manual['url'] = f"https://ivankyo.com/pages/download#{suburl}"
                            manual['source'] = self.name
                            yield manual

    def clean_model_name(self, name):
        cleaned_name = ' '.join(name.split()).replace('&amp;', ',').replace(';', '')
        formatted_names = []
        if ',' in cleaned_name:
            names = cleaned_name.split(',')
            type_name = names[0].split()
            if len(type_name)>1:
                type_name = type_name[0]
            else:
                type_name = ''
            for name in names:
                sep_name = name.split()
                if len(sep_name) > 1:
                    code = sep_name[1]
                else:
                    code = sep_name[0]

                formatted_name = f"{type_name} {code}"
                formatted_names.append(formatted_name.strip())
        else:
            formatted_names.append(cleaned_name)

        return formatted_names
