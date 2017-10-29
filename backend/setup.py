from setuptools import setup, find_packages

setup(
    name='backend',
    version='1.0',
    description='backend',
    scripts=[],
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'worker.d3_task': [
            'make_model_count_top20 = api.d3_task_ext.make_model_count_top20:MakeModelCountTop20',
            'make_model_price_top20 = api.d3_task_ext.make_model_price_top20:MakeModelPriceTop20',
            'make_year_count = api.d3_task_ext.make_year_count:MakeYearCount',
            'year_count = api.d3_task_ext.year_count:YearCount',
            'make_count = api.d3_task_ext.make_count:MakeCount',
        ],
        'worker.train_task': [
            'gradient_boosting_regressor = api.train_task_ext.gradient_boosting_regressor:GradientBoostingRegressorTask',
        ]
    },
    zip_safe=False,
)
