import os
import altair as alt
import pandas as pd
from .base import D3TaskBase
from api.utils import train as train_util
from api.utils import sql as sql_util


class MakeModelCountTop20(D3TaskBase):
    name = 'make_model_count_top20'

    def get_task_signature(self, d3_task):
        return self.get_hash(
            "name:%s" % self.name, "make:%s" % d3_task['data']['make_id'])

    def create_data(self, conn, data):
        # 1. make_model_count_top20: (one file per make; can handle top 20,15,10)
        #    data format: model, count
        # 40 items: 20 largest and 20 smallest

        # select api_ad.model as model, COUNT(api_ad.price) as count
        # from api_ad INNER JOIN api_make
        # where api_ad.make_id = api_make.id and api_make.name = "Toyota"
        # group by api_ad.model
        # order by count DESC
        train_util.validate_required(data, ['make_id', 'make'])
        make_id, make_name = data['make_id'], data['make']

        rs = sql_util.get_count_group_by_make_count(conn, make_id)
        if rs.rowcount > 0:
            models, counts = zip(*rs)
            df = pd.DataFrame({'model': models, 'count': counts})
            chart = alt.Chart(df)
            chart.mark_bar().encode(
                y=alt.Y('count:Q', axis=alt.Axis(title='count')),
                x=alt.X('model:N', axis=alt.Axis(title='model of {0}'.format(make_name)),
                        sort=alt.SortField(field='count', op='values', order='descending')))
            file = os.path.join(self.static_dir, 'd3/make_model_count_top20/{0}.json'.format(make_id))
            os.makedirs(os.path.dirname(file), exist_ok=True)
            with open(file, 'w') as fh:
                fh.write(chart.to_json(indent=2))
