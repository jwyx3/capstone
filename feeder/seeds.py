# query_str = 'auto_transmission=1&auto_transmission=2&bundleDuplicates=1&auto_bodytype=1&auto_bodytype=2&' + \
#             'auto_bodytype=3&auto_bodytype=4&auto_bodytype=5&auto_bodytype=6&auto_bodytype=7&auto_bodytype=8&' + \
#             'auto_bodytype=9&auto_bodytype=10&auto_bodytype=11&auto_bodytype=12&auto_fuel_type=1&' + \
#             'auto_fuel_type=2&auto_fuel_type=3&auto_fuel_type=4&auto_paint=1&auto_paint=2&auto_paint=20&' + \
#             'auto_paint=3&auto_paint=4&auto_paint=5&auto_paint=6&auto_paint=7&auto_paint=8&auto_paint=9&' + \
#             'auto_paint=10&auto_paint=11&auto_title_status=1&auto_title_status=2&auto_title_status=3&' + \
#             'auto_title_status=4&auto_title_status=5&auto_title_status=6&auto_drivetrain=1&auto_drivetrain=2&' + \
#             'auto_drivetrain=3&auto_cylinders=1&auto_cylinders=2&auto_cylinders=3&auto_cylinders=4&' + \
#             'auto_cylinders=5&auto_cylinders=6&auto_cylinders=7&auto_size=1&auto_size=2&auto_size=3&' + \
#             'auto_size=4&condition=10&condition=20&condition=30&condition=40&condition=50&condition=60&' +\
#             'min_price=500&min_auto_year=1990&hasPic=1'

query_str = 'bundleDuplicates=1&min_price=500&min_auto_year=1990&hasPic=1'

seeds_dict = {
    "sfbay_redis:start_urls": [
        'https://sfbay.craigslist.org/search/sby/cta?' + query_str,
        'https://sfbay.craigslist.org/search/scz/cta?' + query_str,
        'https://sfbay.craigslist.org/search/sfc/cta?' + query_str,
        'https://sfbay.craigslist.org/search/pen/cta?' + query_str,
        'https://sfbay.craigslist.org/search/nby/cta?' + query_str,
        'https://sfbay.craigslist.org/search/eby/cta?' + query_str,
    ]
}
