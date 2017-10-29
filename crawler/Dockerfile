FROM python:2.7.14
ADD . /opt/crawler
ADD used_car/settings-prod.py /opt/crawler/used_car/settings.py
RUN set -x && pip install --no-cache-dir -r /opt/crawler/requirements.txt
WORKDIR /opt/crawler
EXPOSE 6023
ENTRYPOINT ["scrapy", "crawl"]
CMD ["sfbay_redis"]
