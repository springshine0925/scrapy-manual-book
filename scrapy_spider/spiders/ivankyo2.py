import scrapy
import json
from scrapy_spider.items import Manual

class IvankyoSpider(scrapy.Spider):
    name = "ivankyo.com11"
    allowed_domains = ["ivankyo.com"]
    start_urls = ["https://ivankyo.com/pages/download#all"]

    def parse(self, response):
        base_url = 'https://admin.ivankyo.com/index.php?route=api/product_downloads/getProductdownloads'

        yield scrapy.Request(url=base_url, callback=self.parse_detail)

    def parse_detail(self, response):
        data = json.loads(response.body)
        for category, items in data.items():
            suburl = '%20'.join(category.split())
               
            for item in items:
                title = item['title']
                clean_model = self.clean_model_name(title)
                if len(clean_model)>1:
                    for model in clean_model:
                        url_list = json.loads(item['url_list'])
                        if isinstance(url_list, dict):
                            for version, urls in url_list.items():
                                url_array = []
                                for url_info in urls:
                                    language = url_info['language']
                                    url = url_info['url']               
                                    url_array.append(url)
                                    break
                                manual = Manual(
                                    model=model,
                                    brand='VANKYO',
                                    product=category,
                                    product_lang= 'en',
                                    file_urls=url_array[0],
                                    type='User Manual',
                                    url=f"https://ivankyo.com/pages/download#{suburl}",
                                    source=self.name
                                )
                                
                                yield manual
                else:
                    model = clean_model[0]
                    url_list = json.loads(item['url_list'])
                    if isinstance(url_list, dict):
                        for version, urls in url_list.items():
                            url_array = []
                            for url_info in urls:
                                language = url_info['language']
                                url = url_info['url']               
                                url_array.append(url)
                                break
                            manual = Manual(
                                model=model,
                                brand='VANKYO',
                                product=category,
                                product_lang= 'en',
                                file_urls=url_array[0],
                                type='User Manual',
                                url=f"https://ivankyo.com/pages/download#{suburl}",
                                source=self.name
                            )
                            
                            yield manual
    def clean_model_name(self, name):
        name = ' '.join(name.split())
        cleaned_name = name.replace('&amp;', ',').replace(';', '')  # Replace "&amp;" with "&" and remove ";"
        formatted_names = []
        if ',' in cleaned_name:
            names = cleaned_name.split(',')  # Split the input string at ',' into a list of names
            type_name = names[0].split()[0]

            for name in names:
                sep_name = name.split()    
                if len(sep_name)>1:
                    code = sep_name[1]
                    formatted_name = f"{type_name} {code}"
                else:
                    code = sep_name[0]
                    formatted_name = code
                # Format the extracted components into the desired format
                
                formatted_names.append(formatted_name) 
        else:
            formatted_names.append(cleaned_name)
        return formatted_names