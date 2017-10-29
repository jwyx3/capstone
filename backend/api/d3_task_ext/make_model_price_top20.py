import os
import altair as alt
import pandas as pd
from sqlalchemy import *
from .base import D3TaskBase
from api.utils import train as train_util
from api.utils import sql as sql_util


class MakeModelPriceTop20(D3TaskBase):
    name = 'make_model_price_top20'

    def get_task_signature(self, d3_task):
        return self.get_hash(
            "name:%s" % self.name, "make:%s" % d3_task['data']['make_id'])

    def create_data(self, conn, data):
        # 2. make_model_price_top20: (one file per make)
        #    data: model, price_mean, price_min, price_max
        # 40 items: 20 largest and 20 smallest

        # select api_ad.model as model, MAX(api_ad.price) as max_price, MIN(api_ad.price) as min_price,
        # AVG(api_ad.price) as mean_price ##, STD(api_ad.price) as std_price
        # from api_ad INNER JOIN api_make
        # where api_ad.make_id = api_make.id and api_make.name = "Toyota"
        # group by api_ad.model
        # order by mean_price ASC

        train_util.validate_required(data, ['make_id', 'make'])
        make_id, make_name = data['make_id'], data['make']

        rs = sql_util.get_price_by_make(conn, make_id)
        if rs.rowcount > 0:
            models, prices = zip(*rs)
            df = pd.DataFrame({'model': models, 'price': prices})
            chart = alt.LayeredChart(df, layers=[alt.Chart().mark_rule().encode(
                x=alt.X('model:N', axis=alt.Axis(title='model of {0}'.format(make_name))),
                y=alt.Y('min(price):Q', axis=alt.Axis(title='min price')),
                y2='max(price):Q',
            ), alt.Chart().mark_tick().encode(
                size=alt.Size(value=5.0),
                x='model:N',
                y=alt.Y('min(price):Q', axis=alt.Axis(title='min price')),
            ), alt.Chart().mark_tick().encode(
                size=alt.Size(value=5.0),
                x='model:N',
                y=alt.Y('max(price):Q', axis=alt.Axis(title='max price')),
            ), alt.Chart().mark_point().encode(
                size=alt.Size(value=2.0),
                x='model:N',
                y=alt.Y('mean(price):Q', axis=alt.Axis(title='mean price')),
            )])

            file = os.path.join(self.static_dir, 'd3/make_model_price_top20/{0}.json'.format(make_id))
            os.makedirs(os.path.dirname(file), exist_ok=True)
            with open(file, 'w') as fh:
                fh.write(chart.to_json(indent=2))
