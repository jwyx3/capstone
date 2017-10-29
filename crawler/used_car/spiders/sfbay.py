# -*- coding: utf-8 -*-
import scrapy
from used_car.items import UsedCarItem


class SfbaySpiderMixin(object):
    # search page:
    #
    # detail_url: '#sortable-results > ul > li:nth-child(n) > p > a::attr(href)'
    # next page: '#searchform > div:nth-child(3) > div.paginator.buttongroup > span.buttons > a.button.next::attr(href)'
    # last page: '#searchform > div:nth-child(3) > div.paginator.buttongroup.lastpage > span.buttons > span::text'

    # detail page:
    #
    # price: response.css('body > section > section > h2 > span.postingtitletext > span.price::text').extract()
    # title: response.css('head > meta[property="og:title"]::attr(content)').extract()

    # postingtitletext: response.css('body > section > section > h2 > span.postingtitletext > :not(.js-only) *::text').extract()
    # postingbody: '#postingbody::text'

    # text of p.attrgroup: response.css('body > section > section > section > div.mapAndAttrs > p:nth-child(n) *::text').extract()
    # notice: response.css('body > section > section > section > ul > li::text').extract()

    # posted time: response.css('body > section > section > section > div.postinginfos > p:nth-child(2) > time::attr(datetime)').extract()

    # images: response.css('#thumbs > a:nth-child(n) > img::attr(href)').extract()
    # thumbs: response.css('#thumbs > a:nth-child(n) > img::attr(src)').extract()

    # postingid: response.css('body > section > section > section > div.postinginfos > p:nth-child(1)::text').re('\d+')

    def parse(self, response):
        if not self.is_last_page(response):
            # follow links to detail pages
            for href in response.css('#sortable-results > ul > li:nth-child(n) > p > a::attr(href)'):
                yield response.follow(href, self.parse_detail)

            # follow pagination links
            for href in response.css(
                    '#searchform > div:nth-child(3) > div.paginator.buttongroup > span.buttons > a.button.next::attr(href)'):
                yield response.follow(href, self.parse)

    @staticmethod
    def is_last_page(response):
        return response.css(
            '#searchform > div:nth-child(3) > div.paginator.buttongroup.lastpage > span.buttons > span::text').extract()

    def is_seen(self, item):
        return False

    def get_collection(self):
        return self.name

    def parse_detail(self, response):
        def extract_with_css(query, pattern=None, index=0):
            if pattern:
                content = response.css(query).re(pattern)
            else:
                content = response.css(query).extract()
            if index >= 0:
                return content[index].strip() if index < len(content) else ''
            return [x.strip() for x in content if x.strip()]

        item = UsedCarItem()
        item['collection'] = self.get_collection()
        item['url'] = response.url
        item['post_id'] = extract_with_css(
            'body > section > section > section > div.postinginfos > p:nth-child(1)::text', pattern='\d+')
        item['title'] = extract_with_css('head > meta[property="og:title"]::attr(content)')
        item['price'] = extract_with_css(
            'body > section > section > h2 > span.postingtitletext > span.price::text', pattern='[\d\.]+')
        item['body'] = ' '.join(extract_with_css('#postingbody::text', index=-1))
        item['images'] = extract_with_css('#thumbs > a:nth-child(n)::attr(href)', index=-1)
        item['thumbs'] = extract_with_css('#thumbs > a:nth-child(n) > img::attr(src)', index=-1)
        item['posted_at'] = extract_with_css(
            'body > section > section > section > div.postinginfos > p:nth-child(2) > time::attr(datetime)')
        if extract_with_css(
                'body > section > section > section > div.postinginfos > p:nth-child(3)::text', pattern='updated:'):
            item['updated_at'] = extract_with_css(
                'body > section > section > section > div.postinginfos > p:nth-child(3) > time::attr(datetime)')
        else:
            item['updated_at'] = item['posted_at']
        item['notice'] = extract_with_css('body > section > section > section > ul > li::text', index=-1)
        item['title_text'] = ' '.join(extract_with_css(
            'body > section > section > h2 > span.postingtitletext > :not(.js-only) *::text', index=-1))
        item['attr_text'] = extract_with_css(
            'body > section > section > section > div.mapAndAttrs > p:nth-child(n) *::text', index=-1)
        item['category'] = extract_with_css(
            'body > section > header.global-header.wide > nav > ul > li.crumb.category > p > a::attr(href)',
            pattern='[^\/]+$')
        item['dealer'] = item['category'] == 'ctd'
        item['address'] = extract_with_css(
            'body > section > section > section > div.mapAndAttrs > div > div.mapaddress::text')
        item['latitude'] = extract_with_css('#map::attr(data-latitude)')
        item['longitude'] = extract_with_css('#map::attr(data-longitude)')

        if not self.is_seen(item):
            yield item


class SfbaySpider(SfbaySpiderMixin, scrapy.Spider):
    name = 'sfbay'
    allowed_domains = ['craigslist.org']
    query_str = 'auto_transmission=1&auto_transmission=2&bundleDuplicates=1&auto_bodytype=1&auto_bodytype=2&' +\
                'auto_bodytype=3&auto_bodytype=4&auto_bodytype=5&auto_bodytype=6&auto_bodytype=7&auto_bodytype=8&' +\
                'auto_bodytype=9&auto_bodytype=10&auto_bodytype=11&auto_bodytype=12&auto_fuel_type=1&' +\
                'auto_fuel_type=2&auto_fuel_type=3&auto_fuel_type=4&auto_paint=1&auto_paint=2&auto_paint=20&' +\
                'auto_paint=3&auto_paint=4&auto_paint=5&auto_paint=6&auto_paint=7&auto_paint=8&auto_paint=9&' +\
                'auto_paint=10&auto_paint=11&auto_title_status=1&auto_title_status=2&auto_title_status=3&' +\
                'auto_title_status=4&auto_title_status=5&auto_title_status=6&auto_drivetrain=1&auto_drivetrain=2&' +\
                'auto_drivetrain=3&auto_cylinders=1&auto_cylinders=2&auto_cylinders=3&auto_cylinders=4&' +\
                'auto_cylinders=5&auto_cylinders=6&auto_cylinders=7&auto_size=1&auto_size=2&auto_size=3&' +\
                'auto_size=4&condition=10&condition=20&condition=30&condition=40&condition=50&condition=60&' + \
                'min_price=500&min_auto_year=1990&hasPic=1'
    start_urls = [
        'https://sfbay.craigslist.org/search/sby/cta?' + query_str,
        'https://sfbay.craigslist.org/search/scz/cta?' + query_str,
        'https://sfbay.craigslist.org/search/sfc/cta?' + query_str,
        'https://sfbay.craigslist.org/search/pen/cta?' + query_str,
        'https://sfbay.craigslist.org/search/nby/cta?' + query_str,
        'https://sfbay.craigslist.org/search/eby/cta?' + query_str,
    ]
