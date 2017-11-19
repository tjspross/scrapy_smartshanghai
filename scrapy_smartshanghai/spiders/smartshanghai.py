# -*- coding: utf-8 -*-
import os
import re
from datetime import datetime as dt

import pandas as pd
import requests
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import TextResponse
from scrapy.selector import Selector


class ScrapySmartshanghaiItem(scrapy.Item):
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


def remove_spaces(str):
    return " ".join(str.split()).encode('utf-8')


class SmartShanghaiHousingSpider(scrapy.Spider):
    name = 'smartshanghai_housing'
    handle_httpstatus_list = [404]

    min_listing = None

    start_urls = ['http://www.smartshanghai.com/housing/']

    def __init__(self, max_prev_listing=None, *args, **kwargs):
        super(SmartShanghaiHousingSpider, self).__init__(*args, **kwargs)

        self.max_prev_listing = max_prev_listing

    def parse(self, response):
        # Get Maximum Current Listings
        houses = response.css(".housing-landing-list").xpath('./a/@href').re(r'.*\/apartments-rent\/([0-9]*$)')
        self.max_current_listings = max(houses)

        # Get Minimum Current Listings
        r = requests.get('http://www.smartshanghai.com/housing/apartments-rent/')
        response = TextResponse(r.url, body=r.text, encoding='utf-8')
        last_page = response.css(".pagination").xpath('./ul/li/a[contains(@href, "page")]/@href').extract()[-1]
        r2 = requests.get(last_page)
        response2 = TextResponse(r2.url, body=r2.text, encoding='utf-8')
        min_current_listing = min(response2.css('.biaoti').xpath("./a/@href").re("\/apartments-rent\/([0-9]*$)"))

        print "CURRENT SMARTSHANGHAI MINIMUM LISTING: %s" % str(min_current_listing)
        print "CURRENT SMARTSHANGHAI MAXIMUM LISTING: %s" % str(min_current_listing)
        print "LOCAL MAXIMUM LISTING: %s" % str(self.max_prev_listing)

        if self.max_prev_listing is None:
            print 'NO LOCAL listings: Pulling from current minimum listing: %s' % min_current_listing
            yield response.follow(self.start_urls[0] + "apartments-rent/%s" % str(min_current_listing),
                                  self.parse_rent)
        elif int(self.max_prev_listing) >= int(min_current_listing) & int(self.max_prev_listing) < int(self.max_current_listings):
            print 'Local Listings AVAILABLE: Pulling from previous maximum listing: %s' % self.max_prev_listing
            yield response.follow(self.start_urls[0] + "apartments-rent/%s" % str(int(self.max_prev_listing) + 1),
                                  self.parse_rent)

        else:
            print "DOING NOTHING - MINIMUM CURRENT LISTING:%s, MINIMUM PREVIOUS LISTING: %s" % (
                min_current_listing, self.max_prev_listing)

    def parse_rent(self, response):
        item = ScrapySmartshanghaiItem()

        item['listing_id'] = re.match('[^0-9]*\/([0-9]*)', response.url).group(1)

        heading = response.xpath('//div[@id="content-listing"]').xpath('.//div[@class="tupian"]//div[@class="wenzi"]')
        item['author'] = heading.xpath('./a/text()').extract_first()
        item['title'] = response.xpath('.//div[@class="mingzi"]/text()').extract_first()
        item['view_count'] = response.xpath('//div[@class="qiyexinxi"]/ul/li/text()').re_first('([0-9]*)')
        item['scrape_time'] = str(dt.utcnow())

        publish_time = heading.xpath('./text()').re_first('([a-zA-Z]*\s{1,2}[0-9]{1,2}, [0-9]{4,}.*)')
        if publish_time:
            publish_time = re.sub(' +', ' ', publish_time)
            item['publish_time'] = dt.strptime(publish_time, '%B %d, %Y, at %H:%M %p')

        def grab_second_div(value, search_re=None, xpath=None):
            for divpair in response.xpath('.//div[@class="xinxi"]/ul/li').extract():
                if re.search(search_re, divpair):
                    newresponse = Selector(text=divpair)
                    item[value] = remove_spaces("".join(newresponse.xpath(xpath).extract()))

        grab_second_div(value='metro', search_re='METRO:', xpath='//div[@class="wenzi station"]/text()')
        grab_second_div(value='price', search_re='PRICE:', xpath='//div[@class="wenzi"]/text()')
        grab_second_div(value='area', search_re='AREA:', xpath='//div[@class="wenzi"]/text()')
        grab_second_div(value='rooms', search_re='ROOMS:', xpath='//div[@class="wenzi"]/text()')
        grab_second_div(value='compound', search_re='COMPOUND:', xpath='//div[@class="wenzi"]/text()')
        grab_second_div(value='size', search_re='SIZE:', xpath='//div[@class="wenzi"]/text()')
        grab_second_div(value='floor', search_re='FLOOR:', xpath='//div[@class="wenzi"]/text()')
        grab_second_div(value='area', search_re='AREA:', xpath='//div[@class="wenzi"]/text()')
        grab_second_div(value='posted_type', search_re='TYPE:', xpath='//div[@class="wenzi"]/text()')
        grab_second_div(value='metro', search_re='METRO:', xpath='//div[@class="wenzi"]/text()')

        for divpair in response.xpath('.//div[@class="link"]').extract():
            if re.search('Description', divpair):
                newresponse = Selector(text=divpair)
                item['description'] = "".join(newresponse.xpath('//div[@class="wenzi"]/text()').extract()).encode(
                    'utf-8'
                )

        for resp in response.xpath('//script'):
            item['latitude'] = resp.re_first(r"[^//]var latitude = ([0-9\.]*)")
            item['longitude'] = resp.re_first(r"[^//]var longitude = ([0-9\.]*)")

        for a in response.xpath('.//div[@class="fast-navigation"]/ul/li[@class="silver"]/text()').extract():
            key = a.lower().strip().replace('-', '_').replace(' ', '_')
            item[key] = 0
        for a in response.xpath('.//div[@class="fast-navigation"]/ul/li[@class="black"]/text()').extract():
            key = a.lower().strip().replace('-', '_').replace(' ', '_')
            item[key] = 1

        if item['listing_id'] < self.max_current_listings:
            yield item
            yield response.follow(self.start_urls[0] + "apartments-rent/%s" % str(int(item['listing_id']) + 1),
                                  self.parse_rent)


def run_crawler():
    file_path = os.getcwd() + "/housing.json"

    if os.path.exists(file_path):
        df = pd.read_json(file_path, lines=True)
        max_prev_listing = df.listing_id.max()
        print max_prev_listing

    else:
        max_prev_listing = None

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'jsonlines',
        'FEED_URI': file_path
    })

    spider = SmartShanghaiHousingSpider(max_prev_listing=max_prev_listing)
    process.crawl(spider, max_prev_listing=max_prev_listing)
    process.start()


if __name__ == "__main__":
    run_crawler()
