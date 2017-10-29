from __future__ import absolute_import, unicode_literals
from django.conf import settings
from backend import celery_app
from .utils import train as train_util
from .utils import sql as sql_util
from .utils import mongo as mongo_util
from .utils import client as api_util
from stevedore import extension, driver
from celery.schedules import crontab
import bson.json_util as bson
import logging
import datetime


app_scheme = settings.APP_SCHEME
app_host = settings.APP_HOST
app_port = settings.APP_PORT
app_worker_token = settings.APP_WORKER_TOKEN

train_min_samples = getattr(settings, 'TRAIN_MIN_SAMPLES', 10)
worker_d3_task_dispatch_period = settings.WORKER_D3_TASK_DISPATCH_PERIOD

make_model = train_util.load_make_model()
models_mapping = train_util.load_models_mapping(make_model)
makes_mapping = train_util.load_makes_mapping(make_model, models_mapping)


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def predict(self, ad):
    train_util.validate_required(ad, ['make_id', 'model_id', 'make', 'model'])

    # run model to get predict price
    sql_conn = sql_util.get_conn()
    mongo_conn = mongo_util.get_conn()

    # get predict_model in mysql: TODO: update
    predict_model_oid = None
    result = sql_util.get_predict_model_by_make_model(sql_conn, ad['make_id'], ad['model_id'])
    for oid, in result:
        predict_model_oid = oid
        break
    if not predict_model_oid:
        logging.info("no model is found and skip predict")
        return

    # get model itself from mongo
    best_model = mongo_util.find_best_train_model_by_id(mongo_conn, predict_model_oid)

    # use ad and get predicted price use driver
    driver_name = best_model['alg_driver']
    mgr = driver.DriverManager(
        namespace='worker.train_task',
        name=driver_name,
        invoke_on_load=True)

    # get predict_price
    predict_price = mgr.driver.predict(ad, best_model)[0]

    # update mysql to add predict price
    sql_util.update_predict_price_by_post_url(sql_conn, predict_price, ad['post_url'], best_model)


@celery_app.task(bind=True)
def train_model(self, data):
    train_util.validate_required(data, ['make_id', 'make', 'model_id', 'model'])

    # TODO: validate data
    sql_conn = sql_util.get_conn()
    mongo_conn = mongo_util.get_conn()

    logging.info("train model of %s, %s", data['make'], data['model'])
    try:
        mgr = extension.ExtensionManager(
            namespace='worker.train_task',
            invoke_on_load=True,
            propagate_map_exceptions=True,
            invoke_args=(train_min_samples,),
        )
        mgr.map(lambda ext, x: ext.obj.train_model(sql_conn, mongo_conn, x), data)

    except Exception:
        logging.error('failed to train model: %s, %s', data['make'], data['model'], exc_info=1)
        raise


@celery_app.task
def dispatch_train_task():
    # periodically task
    # read make and model from mysql
    # create train task for each make and model task
    sql_conn = sql_util.get_conn()
    for make_id, make, model_id, model in sql_util.get_make_model(sql_conn):
        train_model.delay({
            'make_id': make_id, 'make': make,
            'model_id': model_id, 'model': model
        })


# use server api to create ad
@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def import_ad(self, post_url, token):
    api_client = api_util.get_client()
    mongo_conn = mongo_util.get_conn()

    logging.info("connect to mongo db")
    post = mongo_util.find_raw_post_by_post_url(mongo_conn, post_url)
    if not post:
        logging.warning('post is not found and skip it: %s', post_url)
        return

    logging.info("convert post into used car object")
    try:
        used_car = train_util.get_used_car(post, makes_mapping, models_mapping)
    except Exception:
        logging.error("failed to convert to used car object: %s", post_url, exc_info=1)
        raise

    if not used_car:
        logging.warning("format of post is not valid and drop it: %s", post_url)
        return

    logging.info("get make url")
    make_name = api_util.capitalize_make_name(used_car.make)
    makes = api_util.list_makes_by_name(api_client, make_name, token)
    if not makes:
        logging.info("No such make (%s) in our db and skip it", make_name)
        return
    make_url = makes[0]['url']
    make_id = make_url.strip('/').split('/')[-1]

    logging.info("get model url")
    model_name = used_car.model
    models = api_util.list_models_by_make_model_name(api_client, make_url, model_name, token)
    if not models:
        logging.info("No such model (%s) in our db and skip it", model_name)
        return
    model_url = models[0]['url']
    model_id = model_url.strip('/').split('/')[-1]

    logging.info("convert to ad")
    ad = used_car.to_ad(make_url, model_url)
    if not ad:
        logging.warning("the data is not complete and drop it: %s", used_car.post_url)
        return

    # insert into mysql using api
    logging.info("insert into mysql")
    try:
        api_util.create_ad_if_not_exists(api_client, ad, token)
    except Exception:
        logging.error('failed to insert ad and retry: %s', ad['post_url'], exc_info=1)
        raise

    # insert into train data
    logging.info("insert into train data set")
    try:
        train_ad = used_car.to_train_post(
            make_id=make_id, make=make_name,
            model_id=model_id, model=model_name)
        if train_ad:
            mongo_util.upsert_train_post(mongo_conn, train_ad)
    except Exception:
        logging.error('failed to insert training data: %s', ad['post_url'], exc_info=1)
        raise

    # mark related task as dirty or create a new one
    logging.info("create or mark d3 task as dirty")
    try:
        mgr = extension.ExtensionManager(
            namespace='worker.d3_task',
            invoke_on_load=True,
            propagate_map_exceptions=True,
        )
        task_data = {
            'data': {
                'make_id': make_id, 'make': make_name,
                'model_id': model_id, 'model': model_name
            }
        }
        mgr.map(lambda ext, x: ext.obj.create_or_mark_dirty(mongo_conn, x), task_data)
    except Exception:
        logging.error('failed to mark d3 task as dirty and retry: %s', ad['post_url'], exc_info=1)
        raise

    # used by train and predict
    ad.update({
        'make': make_name, 'make_id': make_id,
        'model': model_name, 'model_id': model_id
    })

    logging.info("trigger a predict task")
    predict.delay(ad)


@celery_app.task(bind=True)
def create_d3_data(self, d3_task_str):
    # read mysql and generate csv
    # 1) dirty
    # 2) name
    # 3) data
    # 3) executed_at
    # 4) _id

    d3_task = bson.loads(d3_task_str)
    if not d3_task['dirty']:
        return

    sql_conn = sql_util.get_conn()
    mongo_conn = mongo_util.get_conn()

    # run create_data() of related extension based on name,
    # passing in mysql connection, name, data
    # each one will generate json under static/
    # Let's re-use the same database as before

    # TODO: load driver in worker level
    logging.info("start d3 task")
    mgr = driver.DriverManager(
        namespace='worker.d3_task',
        name=d3_task['name'],
        invoke_on_load=True,
    )
    # TODO: add db connection into worker
    mgr.driver.create_data(sql_conn, d3_task['data'])

    # update dirty and executed_at
    logging.info("update d3 task")
    mongo_util.find_d3_task_and_update(mongo_conn, d3_task['_id'])


@celery_app.task
def dispatch_d3_task():
    # periodically task
    # use mongo to save different csv generate task
    mongo_conn = mongo_util.get_conn()
    for d3_task in mongo_util.find_dirty_d3_tasks(mongo_conn):
        # use string to avoid bson serialization issue
        create_d3_data.delay(bson.dumps(d3_task))


# https://stackoverflow.com/questions/41119053/connect-new-celery-periodic-task-in-django
@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        datetime.timedelta(seconds=worker_d3_task_dispatch_period), dispatch_d3_task.s(),
        name='dispatch d3 task')

    sender.add_periodic_task(
        crontab(hour=1, minute=0, day_of_week=1),
        dispatch_train_task.s(),
        name='dispatch train task')
