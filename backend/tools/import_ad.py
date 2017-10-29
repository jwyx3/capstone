import os
import logging
import requests
import json
from django.conf import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'


session = requests.Session()

api = 'http://localhost:8000/ads/import_ad/'

token = '010c5e0b608fa3df4acd9b4866f8da0f689d8c67' # settings.APP_WORKER_TOKEN

with open(os.path.join(os.path.dirname(__file__), '../data/sfbay2.json'), 'r') as fh:
    for post_json in fh:
        try:
            post = json.loads(post_json)
            resp = session.post(
                api, headers={
                    'Authorization': 'Token %s' % token,
                    'Content-Type': 'application/json'
                },
                data=json.dumps(post))
            if resp.status_code not in [200, 201, 204]:
                logging.error("failed: {0.status_code}, {0.content}".format(resp))
        except Exception:
            logging.error("failed to import: {0}".format(post_json), exc_info=1)
