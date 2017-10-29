from __future__ import absolute_import, unicode_literals
from django.conf import settings
import pymongo
import logging
import datetime
import bson

mongo_server = getattr(settings, 'MONGODB_SERVER', 'localhost')
mongo_port = getattr(settings, 'MONGODB_PORT', 27017)
mongo_db = getattr(settings, 'MONGODB_DB', 'used_car')

mongo_raw_posts = getattr(settings, 'MONGODB_RAW_POSTS', 'sfbay_redis')
mongo_train_posts = getattr(settings, 'MONGODB_TRAIN_POSTS', 'sfbay_train')
mongo_d3_task = getattr(settings, 'MONGODB_D3_TASK', 'sfbay_d3_task')
mongo_train_model = getattr(settings, 'MONGODB_MODEL', 'sfbay_model')


def get_conn():
    return pymongo.MongoClient(mongo_server, mongo_port)


def get_coll(conn, coll):
    return conn[mongo_db][coll]


def get_d3_task_coll(conn):
    return get_coll(conn, mongo_d3_task)


def get_train_posts_coll(conn):
    return get_coll(conn, mongo_train_posts)


def get_raw_posts_coll(conn):
    return get_coll(conn, mongo_raw_posts)


def get_train_model_coll(conn):
    return get_coll(conn, mongo_train_model)


# TODO: add post_url as index
def find_raw_post_by_post_url(conn, post_url):
    raw_posts_coll = get_raw_posts_coll(conn)
    return raw_posts_coll.find_one({"url": post_url})


def upsert_train_post(conn, ad):
    train_posts_coll = get_train_posts_coll(conn)
    result = train_posts_coll.replace_one({'post_url': ad['post_url']}, ad, upsert=True)
    if result.matched_count > 0:  # existing doc
        logging.warning("update existing train data: %s", ad['post_url'])


def find_d3_task_and_update(conn, oid):
    d3_task_coll = get_d3_task_coll(conn)
    d3_task_coll.find_one_and_update({'_id': oid}, {
        '$set': {'dirty': False, 'executed_at': datetime.datetime.utcnow()}})


def find_dirty_d3_tasks(conn):
    d3_task_coll = get_d3_task_coll(conn)
    return d3_task_coll.find({"dirty": True}).sort('executed_at', pymongo.ASCENDING)


def find_best_train_model_by_id(conn, oid):
    if isinstance(oid, str):
        oid = bson.objectid.ObjectId(oid)
    train_model_coll = get_train_model_coll(conn)
    return train_model_coll.find_one({"_id": oid})


def find_train_posts_by_make_model(conn, make_id, model_id):
    train_posts_coll = get_train_posts_coll(conn)
    return train_posts_coll.find({'make_id': make_id, 'model_id': model_id})


def replace_train_model_by_sig(conn, alg_data):
    train_model_coll = get_train_model_coll(conn)
    return train_model_coll.replace_one({'sig': alg_data['sig']}, alg_data, upsert=True)


def find_best_train_model_by_make_model(conn, make_id, model_id):
    train_model_coll = get_train_model_coll(conn)
    cursor = train_model_coll\
        .find({'make_id': make_id, 'model_id': model_id})\
        .sort([('r2_score', pymongo.DESCENDING)])\
        .limit(1)
    for x in cursor:
        return x
    return None


def replace_d3_task(conn, d3_task):
    d3_task_coll = get_d3_task_coll(conn)
    return d3_task_coll.replace_one({
        'sig': d3_task['sig']
    }, dict({
        k: v for k, v in d3_task.items() if k not in ('executed_at',)
    }), upsert=True)
