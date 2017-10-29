from selenium import webdriver
from selenium.webdriver.support.ui import Select
import os
import time
import json


def parse(url):
    driver.get(url)
    time.sleep(5)
    make, model = url.split('/')[-3:-1]
    year_tags = driver.find_elements_by_css_selector(
        '#years-slider-module > div > div.slider-wrapper > div > a:nth-child(n)')
    for year_index in xrange(len(year_tags)):
        year_tag = driver.find_element_by_css_selector(
            '#years-slider-module > div > div.slider-wrapper > div > a:nth-child({})'.format(year_index + 1))
        year = year_tag.text
        year_tag.click()
        time.sleep(5)
        select_trim_tag = driver.find_element_by_css_selector('#amy-trim-list-form > span > select')
        trim_options = [x for x in select_trim_tag.find_elements_by_tag_name("option")]
        trim_values = [
            (element.get_attribute('value'), element.get_attribute('data-id'))
            for element in trim_options if element.get_attribute('value')
        ]
        print(trim_values)
        for trim, id in trim_values:
            select_trim = Select(driver.find_element_by_css_selector('#amy-trim-list-form > span > select'))
            select_trim.select_by_value(trim)
            time.sleep(5)
            item = {
                'year': year,
                'make': make,
                'model': model,
                'trim': trim,
                'msrp': driver.find_element_by_css_selector(
                    '#main > div > div.amy-module > div > div.amy-car-content > div.amy-bottom-content > div.amy-car-price > div.amy-msrp-price > span').text
            }
            specs = driver.find_elements_by_css_selector('#at-a-glance-module > div.at-a-glance-info-list > a:nth-child(n) span')
            item.update(dict(zip([x.text.lower() for x in specs[::2]], [y.text for y in specs[1::2]])))
            print(item)
            yield item


if __name__ == '__main__':

    profile = webdriver.FirefoxProfile()
    profile.set_preference(
        "general.useragent.override",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36")
    driver = webdriver.Firefox(profile)

    urls = []
    with open(os.path.join(os.path.dirname(__file__), '../data/detail_urls.txt'), 'r') as fh:
        for line in fh:
            urls.append(line.strip())
    items = [item for url in urls for item in parse(url)]

    with open(os.path.join(os.path.dirname(__file__), '../data/detail.txt'), 'w') as fh:
        for item in items:
            fh.write(json.dumps(item) + "\n")
