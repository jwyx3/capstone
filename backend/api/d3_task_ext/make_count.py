import os
import altair as alt
import pandas as pd
from .base import D3TaskBase
from api.utils import sql as sql_util


class MakeCount(D3TaskBase):
    name = 'make_count'

    def create_data(self, conn, data):
        rs = sql_util.get_count_group_by_make(conn)
        if rs.rowcount > 0:
            makes, counts = zip(*rs)
            df = pd.DataFrame({'make': makes, 'count': counts})
            chart = alt.Chart(df)
            chart.mark_bar().encode(
                y=alt.Y('count:Q'),
                x=alt.X('make:N'))
            file = os.path.join(self.static_dir, 'd3/make_count.json')
            os.makedirs(os.path.dirname(file), exist_ok=True)
            with open(file, 'w') as fh:
                fh.write(chart.to_json(indent=2))
