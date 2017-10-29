# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from scrapy.conf import settings
import requests
import json
import logging


app_scheme = settings['APP_SCHEME']
app_host = settings['APP_HOST']
app_port = settings['APP_PORT']
app_worker_token = settings['APP_WORKER_TOKEN']


def get_api_url(path):
    return "{0}://{1}:{2}{3}".format(app_scheme, app_host, app_port, path)


class UsedCarPipeline(object):
    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'], settings['MONGODB_PORT'])
        db = connection[settings['MONGODB_DB']]
        self.collections = {
            "sfbay": db['sfbay'],
            "sfbay_redis": db['sfbay_redis'],
        }
        for coll in self.collections:
            db[coll].create_index("post_id", unique=True)

        self.session = requests.Session()

    @staticmethod
    def format_attr(attr_text):
        result = []
        for i in xrange(len(attr_text)):
            if i > 0 and ':' in attr_text[i - 1] and ':' not in attr_text[i]:
                result.append('*%s*' % attr_text[i])
            else:
                result.append(attr_text[i])
        return ' '.join(result)

    def get_message(self, item):
        return {
            "attachments": [
                {
                    "color": "#36a64f",
                    "title": item['attr_text'][0] + " - $" + item['price'],
                    "title_link": item['url'],
                    "text": self.format_attr(item['attr_text'][1:]),
                    "footer": ['owner', 'dealer'][item['dealer']]
                }
            ]
        }

    def post_message(self, item):
        if not settings['ENABLE_SLACK']:
            return
        resp = self.session.post(
            settings['SLACK_WEBHOOK'],
            headers={"Content-type": "application/json"},
            data=json.dumps(self.get_message(item)),
            verify=False
        )
        logging.info("post to slack: %s" % resp)

    def process_item(self, item, spider):
        if 'collection' in item:
            result = self.collections[item['collection']].replace_one(
                {'post_id': item['post_id']}, dict(item), upsert=True)
            if result.matched_count == 0:  # new doc
                # self.post_message(item)
                try:
                    resp = self.session.post(
                        get_api_url("/ads/import_ad/"),
                        data=json.dumps({'post_url': item['url']}),
                        headers={
                            'Content-Type': 'application/json',
                            'Authorization': 'Token %s' % app_worker_token,
                        })
                    if not (200 <= resp.status_code < 300):
                        raise Exception(
                            "failed to import ad: {0.status_code}, {0.content}".format(resp))
                    logging.info("saved one ad: %s", item['url'])
                except Exception:
                    logging.error("failed to import ad: {0}".format(
                        item['url']), exc_info=1)
        return item
