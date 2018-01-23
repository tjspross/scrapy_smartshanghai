# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import os
from datetime import datetime

import pandas as pd
from scrapy.exceptions import DropItem


def myconverter(o):
    if isinstance(o, datetime):
        return o.__str__()


class ScrapySmartShanghaiPipeline(object):
    def __init__(self):
        self.file_path = os.path.dirname(os.path.dirname(__file__)) + "/output/listings.jl"

        df = pd.read_json(self.file_path, lines=True)
        if df.empty:
            self.ids_seen=set()
        else:
            self.ids_seen = set(df.listing_id)

    def open_spider(self, spider):
        self.file = open(self.file_path, 'a')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        if item['listing_id'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        elif item['author'] is None:
            raise DropItem("Null listing found: %s" % item)
        else:
            self.ids_seen.add(item['listing_id'])
            if self.ids_seen:
                line = "\n" + json.dumps(dict(item), default=myconverter)
            else:
                line = json.dumps(dict(item), default=myconverter)
            self.file.write(line)
            return item