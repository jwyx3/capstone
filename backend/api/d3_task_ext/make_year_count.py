import os
import altair as alt
import pandas as pd
from .base import D3TaskBase
from api.utils import train as train_util
from api.utils import sql as sql_util


class MakeYearCount(D3TaskBase):
    name = 'make_year_count'

    def get_task_signature(self, d3_task):
        return self.get_hash(
            "name:%s" % self.name, "make:%s" % d3_task['data']['make_id'])

    def create_data(self, conn, data):
        # 4. make_model_year_count: (one file per make)
        #    data: model, year, count

        # select api_ad.year as year, COUNT(api_ad.price) as count
        # from api_ad
        # where api_ad.make_id = "Toyota"
        # group by year
        # order by year ASC
        train_util.validate_required(data, ['make_id', 'make'])

        make_id, make_name = data['make_id'], data['make']
        rs = sql_util.get_year_group_by_make(conn, make_id)
        if rs.rowcount > 0:
            years, counts = zip(*rs)
            df = pd.DataFrame({'year': years, 'count': counts})
            chart = alt.Chart(df)
            chart.mark_bar().encode(
                y=alt.Y('count:Q'),
                x=alt.X('year:O', axis=alt.Axis(title='year of {0}'.format(make_name)),
                        scale=alt.Scale(domain=list(range(int(df['year'].min()), int(df['year'].max()) + 1)))))
            file = os.path.join(self.static_dir, 'd3/make_year_count/%s.json' % make_id)
            os.makedirs(os.path.dirname(file), exist_ok=True)
            with open(file, 'w') as fh:
                fh.write(chart.to_json(indent=2))
