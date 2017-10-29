from __future__ import absolute_import, unicode_literals
from django.conf import settings
import json
import requests
import logging

app_scheme = settings.APP_SCHEME
app_host = settings.APP_HOST
app_port = settings.APP_PORT
app_worker_token = settings.APP_WORKER_TOKEN


def get_client():
    return requests.Session()


def get_api_url(path):
    return "{0}://{1}:{2}{3}".format(app_scheme, app_host, app_port, path)


def capitalize_make_name(make):
    return ' '.join([x.capitalize() for x in make.split('-')])


def list_makes_by_name(client, name, token=None):
    resp = client.get(
        get_api_url('/makes/'), params={
            'name': name,
        }, headers={
            'Authorization': 'Token %s' % token,
            'Content-Type': 'application/json'
        })
    rs = resp.json()['results']
    return rs


def list_models_by_make_model_name(client, make, model_name, token=None):
    resp = client.get(
        get_api_url('/models/'), params={
            'name': model_name,
            'make': make,
        }, headers={
            'Authorization': 'Token %s' % token,
            'Content-Type': 'application/json'
        })
    rs = resp.json()['results']
    return rs


def create_ad_if_not_exists(client, ad, token=None):
    post_url = ad['post_url']

    resp = client.get(
        get_api_url("/ads/"),
        params={'post_url': post_url},
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Token %s' % token,
        })
    if not (200 <= resp.status_code < 300):
        raise Exception("failed to filter ad: {0.status_code}, {0.content}".format(resp))

    data = resp.json()
    if len(data['results']) == 0:
        logging.info("no such ad and create one: %s", post_url)
        resp = client.post(
            get_api_url("/ads/"),
            data=json.dumps(ad),
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Token %s' % token,
            })
        if not (200 <= resp.status_code < 300):
            raise Exception("failed to create ad: {0.status_code}, {0.content}".format(resp))
