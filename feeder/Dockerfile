FROM python:3.6.3
ADD crontab /etc/cron.d/feeder
ADD feeder.py requirements.txt seeds.py /opt/feeder/
RUN set -x\
    && apt-get update && apt-get -y install cron\
    && pip install --no-cache-dir -r /opt/feeder/requirements.txt\
    && chmod 0644 /etc/cron.d/feeder && touch /var/log/cron.log
WORKDIR /opt/feeder
CMD cron && tail -f /var/log/cron.log
