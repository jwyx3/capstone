from selenium import webdriver
from selenium.webdriver.support.ui import Select
import os
import time

if __name__ == '__main__':

    start_url = 'http://www.msn.com/en-us/autos'

    profile = webdriver.FirefoxProfile()
    profile.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36")
    driver = webdriver.Firefox(profile)

    detail_urls = []

    # construct detail page urls
    driver.get(start_url)
    time.sleep(5)
    select_age = Select(driver.find_element_by_id('findacar-age'))
    select_age.select_by_value('both')
    time.sleep(5)
    select_makes_tag = driver.find_element_by_id("findacar-makes")
    make_options = [x for x in select_makes_tag.find_elements_by_tag_name("option")]
    make_values = [element.get_attribute('value') for element in make_options]
    print(make_values)
    select_makes = Select(select_makes_tag)
    for make in make_values:
        if not make.startswith('sponsored'):
            select_makes.select_by_value(make)
            time.sleep(5)
            select_models_tag = driver.find_element_by_id("findacar-models")
            model_options = [x for x in select_models_tag.find_elements_by_tag_name("option")]
            model_values = [
                (element.get_attribute('value'), element.get_attribute('data-id'))
                for element in model_options if element.get_attribute('data-id')
            ]
            print(model_values)
            for model, id in model_values:
                url = "{}/{}/{}/sd-{}".format(start_url, make, model, id)
                detail_urls.append(url)

    with open(os.path.join(os.path.dirname(__file__), '../data/detail_urls.txt'), 'w') as fh:
        for url in detail_urls:
            fh.write(url + "\n")
