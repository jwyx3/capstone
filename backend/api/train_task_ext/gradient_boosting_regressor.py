import os
import altair as alt
import pandas as pd
from sqlalchemy import *
from .base import TrainTaskBase
from sklearn.ensemble import GradientBoostingRegressor


class GradientBoostingRegressorTask(TrainTaskBase):
    name = 'GradientBoostingRegressor'

    def get_alg(self):
        return GradientBoostingRegressor(
            random_state=10, n_estimators=500, learning_rate=0.01, min_samples_split=4,
            min_samples_leaf=2, loss='ls')
