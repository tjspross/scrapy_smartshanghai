# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ScrapySmartShanghaiItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    posted_type = scrapy.Field()
    listing_id = scrapy.Field()
    view_count = scrapy.Field()
    scrape_time = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    floor = scrapy.Field()
    metro = scrapy.Field()
    size = scrapy.Field()
    author = scrapy.Field()
    area = scrapy.Field()
    compound = scrapy.Field()
    publish_time = scrapy.Field()
    description = scrapy.Field()
    furnished = scrapy.Field()
    rooms = scrapy.Field()
    price = scrapy.Field()
    title = scrapy.Field()

    # Utilities
    washing_machine = scrapy.Field()
    parking = scrapy.Field()
    tv = scrapy.Field()
    central_aircon = scrapy.Field()
    security = scrapy.Field()
    balcony = scrapy.Field()
    elevator = scrapy.Field()
    playground = scrapy.Field()
    oven = scrapy.Field()
    dryer = scrapy.Field()
    dvd_player = scrapy.Field()
    health_club = scrapy.Field()
    pool = scrapy.Field()
    outdoor_space = scrapy.Field()
    air_filter = scrapy.Field()
    water_filter = scrapy.Field()
    floor_heating = scrapy.Field()
    wall_heating = scrapy.Field()