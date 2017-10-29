import os
import collections
import requests
import json
from django.conf import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'

make_model = collections.defaultdict(set)

with open(os.path.join(os.path.dirname(__file__), '../data/model_synonym.txt'), 'r') as fh:
    for line in fh:
        make, model = line.strip().split(',')[:2]
        make_model[make].add(model)


make_api = 'http://localhost:8000/makes/'
model_api = 'http://localhost:8000/models/'
token = '010c5e0b608fa3df4acd9b4866f8da0f689d8c67' #settings.APP_WORKER_TOKEN

session = requests.Session()

for make, models in make_model.items():
    resp = session.post(
        make_api, headers={
            'Authorization': 'Token %s' % token,
            'Content-Type': 'application/json'
        },
        data=json.dumps({'name': make}))
    make = resp.json()['url']
    print(resp.status_code, resp.content)
    for model in models:
        resp = session.post(
            model_api, headers={
                'Authorization': 'Token %s' % token,
                'Content-Type': 'application/json'
            },
            data=json.dumps({'name': model, 'make': make}))
        print(resp.status_code, resp.content)
