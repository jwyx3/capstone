# -*- coding: utf-8 -*-
import scrapy


class TestProxySpider(scrapy.Spider):
    name = 'test_proxy'
    allowed_domains = ['www.toolsvoid.com']
    start_urls = ['http://www.toolsvoid.com/what-is-my-ip-address']

    def parse(self, response):
        yield {
            'IP Address': response.css('body > section.articles-section > div > div > div > div.col-md-8.display-flex > div > div.table-responsive > table *::text').re('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
        }
