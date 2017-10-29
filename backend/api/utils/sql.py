from __future__ import absolute_import, unicode_literals
from django.conf import settings
from datetime import datetime
from sqlalchemy import *

MY_DB_NAME = settings.DATABASES['default']['NAME']
MY_USER = settings.DATABASES['default']['USER']
MY_PASSWORD = settings.DATABASES['default']['PASSWORD']
MY_HOST = settings.DATABASES['default']['HOST']
MY_PORT = settings.DATABASES['default']['PORT']


def get_conn():
    # return create_engine('sqlite:////home/vagrant/workspace/capstone1/backend/db.sqlite3')
    return create_engine('mysql://{0}:{1}@{2}:{3}/{4}'.format(
        MY_USER, MY_PASSWORD, MY_HOST, MY_PORT, MY_DB_NAME))


def get_make_model(conn):
    query = text(
        "select api_make.id as make_id, api_make.name as make_name, " +
        "api_carmodel.id as model_id, api_carmodel.name as model_name " +
        "from api_make INNER JOIN api_carmodel " +
        "where api_make.id = api_carmodel.make_id"
        )
    return conn.engine.execute(query)


def get_predict_model_by_make_model(conn, make_id, model_id):
    query = text(
        "select predict_model " +
        "from api_carmodel " +
        "where make_id = {0} and id = {1}".format(make_id, model_id)
    )
    return conn.engine.execute(query)


def update_predict_model_by_make_model(conn, oid, make_id, model_id):
    update_stmt = text(
        'update api_carmodel set predict_model = :alg_model_id ' +
        'where id = :model_id and make_id = :make_id')
    rs = conn.engine.execute(update_stmt, {
        'alg_model_id': oid,
        'make_id': make_id,
        'model_id': model_id
    })
    return rs


def update_predict_price_by_post_url(conn, predict_price, post_url, alg_model):
    update_stmt = text(
        'update api_ad set predict_price = :predict_price, predict_info = :predict_info, ' +
        'predicted_at = :predicted_at ' +
        'where post_url = :post_url')
    conn.echo = True
    rs = conn.engine.execute(update_stmt, {
        'predict_price': predict_price,
        'predicted_at': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"),
        'predict_info': "{r2_score},{alg_driver},{created_at}".format(**alg_model),
        'post_url': post_url
    })
    return rs


def get_count_group_by_make(conn):
    query = text(
        "select api_make.name as make, COUNT(api_ad.price) as count " +
        "from api_ad INNER JOIN api_make " +
        "where api_ad.make_id = api_make.id "
        "group by api_ad.make_id ")
    return conn.engine.execute(query)


def get_count_group_by_make_count(conn, make_id):
    query = text(
        "select api_carmodel.name as model, COUNT(api_ad.id) as count " +
        "from api_carmodel INNER JOIN api_ad " +
        "where api_carmodel.id = api_ad.model_id and api_carmodel.make_id = {0} ".format(make_id) +
        "group by api_carmodel.name")
    return conn.engine.execute(query)


def get_price_by_make(conn, make_id):
    query = text(
        "select api_carmodel.name as model, api_ad.price as price " +
        "from api_carmodel INNER JOIN api_ad " +
        "where api_carmodel.id = api_ad.model_id and api_carmodel.make_id = {0} ".format(make_id))
    return conn.engine.execute(query)


def get_year_group_by_make(conn, make_id):
    query = text(
        "select api_ad.year as year, COUNT(api_ad.price) as count " +
        "from api_ad " +
        "where api_ad.make_id = {0} ".format(make_id) +
        "group by api_ad.year")
    return conn.engine.execute(query)


def get_count_group_by_year(conn):
    query = text(
        "select api_ad.year as year, COUNT(api_ad.price) as count " +
        "from api_ad " +
        "group by api_ad.year ")
    return conn.engine.execute(query)
