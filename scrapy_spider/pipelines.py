# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class ScrapySpiderPipeline:
    def process_item(self, item, spider):
        return item

# import csv

# class CSVPipeline:
#     def open_spider(self, spider):
#         self.file = open('output.csv', 'w', newline='', encoding='utf-8')
#         self.exporter = csv.writer(self.file)
#         self.exporter.writerow(['title', 'description'])  # Replace with actual field names

#     def close_spider(self, spider):
#         self.file.close()

#     def process_item(self, item, spider):
#         self.exporter.writerow([item.get('title'), item.get('description')])  # Replace with actual field names
#         return item
