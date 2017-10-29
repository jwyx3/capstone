# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UsedCarItem(scrapy.Item):
    post_id = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    body = scrapy.Field()
    images = scrapy.Field()
    thumbs = scrapy.Field()
    posted_at = scrapy.Field()
    updated_at = scrapy.Field()
    notice = scrapy.Field()
    title_text = scrapy.Field()
    attr_text = scrapy.Field()
    collection = scrapy.Field()
    url = scrapy.Field()
    category = scrapy.Field()
    dealer = scrapy.Field()
    address = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()


class MakeModelItem(scrapy.Item):
    term = scrapy.Field()
