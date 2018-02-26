import os
import re
from datetime import datetime as dt

import pandas as pd
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.spider import CrawlSpider, Rule

from housing.items import ScrapySmartShanghaiItem


def remove_spaces(str):
    return " ".join(str.split()).encode('utf-8')


class HousingSpider(CrawlSpider):
    name = 'ss_housing'
    start_urls = ["http://www.smartshanghai.com/housing/apartments-rent/"]
    allowed_domains = ["smartshanghai.com"]

    file_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + "/output/listings.jl"
    df = pd.read_json(file_path, lines=True)
    # deny_list = ['(\/housing\/apartments\-rent\/%s)' % str(listing_id) for listing_id in df.listing_id]
    # print deny_list

    rules = [
        Rule(
            LinkExtractor(
                allow='/housing/apartments-rent/(.+)',
                # deny=deny_list,
                restrict_css='.left'),
            callback='parse_listing'),
        Rule(
            LinkExtractor(
                allow='page=(\d+)',
                restrict_css='.pagination'))
    ]

    def parse_listing(self, response):
        item = ScrapySmartShanghaiItem()

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

        yield item
