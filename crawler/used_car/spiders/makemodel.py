# -*- coding: utf-8 -*-
import scrapy
import json
import string
import os
from hashlib import sha1
from used_car.items import MakeModelItem


def get_hash(cap, seed):
    def hash(value):
        ret = 0
        for i in range(len(value)):
            ret += seed * ret + ord(value[i])
        return (cap - 1) & ret
    return hash


class BloomFilter(object):
    def __init__(self, size=28):
        self.bit_set = 0
        self.bit_size = 1 << size  # 32M
        self.seeds = [5, 7, 11, 13, 31, 37, 61]
        self.hash_func = [get_hash(self.bit_size, seed) for seed in self.seeds]

    def get_bit(self, pos):
        return self.bit_set & (1 << pos)

    def set_bit(self, pos):
        self.bit_set |= (1 << pos)

    @staticmethod
    def __encode(item):
        x_sha1 = sha1()
        x_sha1.update(item)
        return x_sha1.hexdigest()

    def __contains__(self, item):
        if not item:
            return False
        s = self.__encode(item)
        return all(self.get_bit(f(s)) for f in self.hash_func)

    def add(self, item):
        if not item:
            return
        s = self.__encode(item)
        for f in self.hash_func:
            self.set_bit(f(s))


class MakeModelSpider(scrapy.Spider):
    name = 'makemodel'
    allowed_domains = ['craigslist.org']
    SUGGEST_URL_TEMPLATE = 'https://sfbay.craigslist.org/suggest?v=12&type=makemodel&term={}&cat=cta'

    def __init__(self, *args, **kwargs):
        super(MakeModelSpider, self).__init__(*args, **kwargs)
        self.start_urls = [MakeModelSpider.get_suggest_url(x) for x in string.ascii_lowercase]
        self.bf = BloomFilter()
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/makes_uniq.txt')) as fh:
            for term in fh:
                self.start_urls.append(MakeModelSpider.get_suggest_url(term.strip()))

    def parse(self, response):
        terms = json.loads(response.text)
        for term in terms:
            if term and term not in self.bf:
                self.bf.add(term)
                yield response.follow(self.get_suggest_url(term), self.parse)

                item = MakeModelItem()
                item['term'] = term
                yield item

    @classmethod
    def get_suggest_url(cls, term):
        return cls.SUGGEST_URL_TEMPLATE.format(term.replace(' ', '+'))
