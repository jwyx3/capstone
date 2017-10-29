import abc
import six
import logging
from django.conf import settings
from hashlib import sha1
from api.utils import mongo as mongo_util
from api.utils import train as train_util


@six.add_metaclass(abc.ABCMeta)
class D3TaskBase(object):
    name = 'base'
    static_dir = settings.APP_STATIC_DIR

    @staticmethod
    def get_hash(*args):
        x_sha1 = sha1()
        x_sha1.update('#'.join(args).encode('utf-8'))
        return x_sha1.hexdigest()

    def get_task_signature(self, data):
        return self.get_hash("name:%s" % self.name)

    def create_or_mark_dirty(self, conn, d3_task):
        train_util.validate_required(d3_task['data'], ['make_id', 'make', 'model_id', 'model'])
        d3_task['sig'] = self.get_task_signature(d3_task)
        d3_task['dirty'] = True
        d3_task['name'] = self.name
        result = mongo_util.replace_d3_task(conn, d3_task)
        if result.matched_count == 0:
            logging.info("create new task: %s", d3_task['sig'])
        else:
            logging.info("mark existing task as dirty: %s", d3_task['sig'])

    @abc.abstractclassmethod
    def create_data(self, db, data):
        pass
