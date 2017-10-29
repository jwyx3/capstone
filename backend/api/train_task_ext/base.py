import abc
import six
import logging
import time
import re
import os
import datetime
import pandas as pd
import numpy as np
import altair as alt
import tempfile
from django.conf import settings
from hashlib import sha1
from sklearn.externals import joblib
from sklearn.model_selection import cross_val_score
from api.utils import train as train_util
from api.utils import mongo as mongo_util
from api.utils import sql as sql_util


@six.add_metaclass(abc.ABCMeta)
class TrainTaskBase(object):
    name = 'base'

    def __init__(self, min_num=10, alg_dir=None):
        self.min_num = min_num
        self.min_r2_score = 0.8
        self.alg_dir = alg_dir
        if not self.alg_dir:
            self.alg_dir = os.path.join(settings.APP_STATIC_DIR, 'alg')

    @staticmethod
    def get_hash(*args):
        x_sha1 = sha1()
        x_sha1.update('#'.join(args).encode('utf-8'))
        return x_sha1.hexdigest()

    def get_task_signature(self, data):
        return self.get_hash(
            "alg_driver:%s" % data['alg_driver'],
            "make_id:%s" % data['make_id'],
            "model_id:%s" % data['model_id'],
            "r2_score:%s" % data['r2_score'])

    @staticmethod
    def remove_outliers(df, fields, k=3):
        if not isinstance(fields, list):
            fields = [fields]
        for field in fields:
            if isinstance(df, pd.DataFrame):
                df = df[np.abs(df[field] - df[field].mean()) <= (k * df[field].std())]
            elif isinstance(df, pd.Series):
                df = df[((df - df.mean()).abs() <= k * df.std())]
        return df

    # https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    @staticmethod
    def snake_case(name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @staticmethod
    def without_keys(d, keys):
        return {x: d[x] for x in d if x not in keys}

    def exclude_keys(self, ads):
        return [self.without_keys(x, ['_id', 'make_id', 'make', 'model']) for x in ads]

    @staticmethod
    def dump_model(alg):
        with tempfile.NamedTemporaryFile() as fp:
            joblib.dump(alg, fp.name)
            fp.seek(0)
            return fp.read()

    @staticmethod
    def load_model(model_str):
        with tempfile.NamedTemporaryFile() as fp:
            fp.write(model_str)
            return joblib.load(fp.name)

    @staticmethod
    def drop_features(X):
        excluded = set(['latitude', 'longitude', 'post_url', 'make_id', 'model_id']) & set(X.columns)
        if 'odometer' in X.columns:
            X = X.dropna(subset=['odometer'])
        if 'cylinders' in X.columns:
            X = X.fillna(X['cylinders'].value_counts().index[0])  # filled with most frequent
        X = X.drop(list(excluded), axis=1)
        return X

    @staticmethod
    def to_ohe(df, excluded):
        categoricals = set()
        for col, col_type in df.dtypes.iteritems():
            if col_type == 'O':
                categoricals.add(col)
            else:
                df[col].fillna(0)
        categoricals = categoricals - set(excluded)
        return pd.get_dummies(df, columns=list(categoricals), dummy_na=True)

    @staticmethod
    def add_features(X):
        max_year = X['year'].max() + 1
        X['miles_per_year'] = X['odometer'].astype('float') / (max_year - X['year'])
        X['posted_at'] = X['posted_at'].apply(
            lambda x: time.mktime(datetime.datetime.strptime(x[:-6], "%Y-%m-%dT%H:%M:%S").timetuple()))
        return X

    def transform_features(self, X, columns=None):
        X_ohe = self.to_ohe(X, ['make', 'model'])
        if columns:
            X_ohe = X_ohe.reindex(columns=columns, fill_value=0)
        return X_ohe

    @staticmethod
    def get_score(alg, X, y):
        return cross_val_score(alg, X, y, scoring='r2', cv=3)

    def get_file(self, make_id, model_id):
        make_model_dir = os.path.join(self.alg_dir, '{0}_{1}'.format(make_id, model_id))
        os.makedirs(make_model_dir, exist_ok=True)
        return os.path.join(make_model_dir, self.snake_case(self.name) + '.json')

    def visualize_alg(self, alg_data):
        make_id, make = alg_data['make_id'], alg_data['make']
        model_id, model = alg_data['model_id'], alg_data['model']
        scores, features = zip(*alg_data['feature_importances'])
        data = pd.DataFrame({'make': features, 'count': scores})
        chart = alt.Chart(data)
        chart.mark_bar().encode(
            y=alt.Y('rank:Q'),
            x=alt.X('feature:N', axis=alt.Axis(title='feature of {0}, {1}'.format(make, model))))
        with open(self.get_file(make_id, model_id), 'w') as fh:
            fh.write(chart.to_json(indent=2))

    @abc.abstractclassmethod
    def get_alg(self):
        pass

    def get_driver_name(self):
        return self.snake_case(self.name)

    def predict(self, ads, alg_model_info):
        if not isinstance(ads, (list, tuple)):
            ads = [ads]
        alg = self.load_model(alg_model_info['alg_model'])
        test = pd.DataFrame(self.exclude_keys(ads))
        test = self.drop_features(test)
        test = self.add_features(test)
        test_ohe = self.transform_features(test, alg_model_info.get('columns'))
        X_test = test_ohe[test_ohe.columns.difference(['price'])]
        X_test_norm = X_test
        return alg.predict(X_test_norm)

    def train_model(self, sql_conn, mongo_conn, data):
        train_util.validate_required(data, ['make_id', 'make', 'model_id', 'model'])

        make_id, make = data['make_id'], data['make']
        model_id, model = data['model_id'], data['model']

        # get train data from mongo db
        cursor = mongo_util.find_train_posts_by_make_model(mongo_conn, make_id, model_id)
        train_data = self.exclude_keys(cursor)

        if len(train_data) < self.min_num:
            logging.info("the size of train data is %d (<%d) and skip", len(train_data), self.min_num)
            return

        train = pd.DataFrame(train_data)
        train = self.drop_features(train)
        train = self.add_features(train)

        if len(train) < self.min_num:
            logging.info("the size of cleaned train data is %d (<%d) and skip", len(train), self.min_num)
            return

        train_ohe = self.transform_features(train)
        X_train = train_ohe[train_ohe.columns.difference(['price'])]
        X_train_norm = X_train
        y_train = train_ohe['price']

        predictors = list(set(train_ohe.columns) - set(['price']))

        alg = self.get_alg()
        alg.fit(X_train_norm, y_train)

        alg_model_content = self.dump_model(alg)

        # Perform cross-validation:
        score = self.get_score(alg, X_train_norm, y_train)

        alg_data = {
            'r2_score': score.mean(),
            'feature_importances': sorted(zip(alg.feature_importances_, predictors), key=lambda x: -x[0]),
            'columns': list(train_ohe.columns),
            'size': len(X_train_norm),
            'make_id': make_id,
            'model_id': model_id,
            'make': make,
            'model': model,
            'created_at': time.time(),
            'alg_driver': self.get_driver_name(),
            'alg_model': alg_model_content,
        }
        alg_data['sig'] = self.get_task_signature(alg_data)

        # update mongo db
        result = mongo_util.replace_train_model_by_sig(mongo_conn, alg_data)
        if result.matched_count > 0:  # existing doc
            logging.warning("update existing train data: %s", alg_data['sig'])

        # create importance graph
        self.visualize_alg(alg_data)

        # get the highest score
        result = mongo_util.find_best_train_model_by_make_model(mongo_conn, make_id, model_id)
        if result and result['r2_score'] > self.min_r2_score:
            # update mysql db if it's highest score
            sql_util.update_predict_model_by_make_model(
                sql_conn, str(result['_id']), make_id, model_id)
