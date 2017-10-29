import os
import altair as alt
import pandas as pd
from sqlalchemy import *
from .base import D3TaskBase
from api.utils import sql as sql_util


class YearCount(D3TaskBase):
    name = 'year_count'

    def create_data(self, conn, data):
        rs = sql_util.get_count_group_by_year(conn)
        if rs.rowcount > 0:
            years, counts = zip(*rs)
            df = pd.DataFrame({'year': years, 'count': counts})
            chart = alt.Chart(df)
            chart.mark_bar().encode(
                y=alt.Y('count:Q'),
                x=alt.X('year:O', scale=alt.Scale(domain=list(range(
                    int(df['year'].min()), int(df['year'].max()) + 1)))))
            file = os.path.join(self.static_dir, 'd3/year_count.json')
            os.makedirs(os.path.dirname(file), exist_ok=True)
            with open(file, 'w') as fh:
                fh.write(chart.to_json(indent=2))
