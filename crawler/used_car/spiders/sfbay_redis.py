# -*- coding: utf-8 -*-
from scrapy_redis.spiders import RedisSpider
from sfbay import SfbaySpiderMixin
from used_car.dupefilter import BloomFilter


class SfbayRedisSpider(SfbaySpiderMixin, RedisSpider):
    name = 'sfbay_redis'

    def __init__(self, *args, **kwargs):
        super(SfbayRedisSpider, self).__init__(*args, **kwargs)
        self.bf = None

    def is_seen(self, item):
        if not self.server or not item['images']:
            return False
        if not self.bf:
            self.bf = BloomFilter(self.server, self.name + '_bf_dedup')
        # use redis to handle duplicate
        img = item['images'][0]
        if img not in self.bf:
            self.bf.add(img)
            return False
        return True
