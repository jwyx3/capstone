FROM python:3.6.3
ENV INIT 1
ADD . /opt/backend
ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf
ADD backend/settings-prod.py /opt/backend/backend/settings.py
RUN set -x\
    && apt-get update && apt-get install -y supervisor tcpdump net-tools vim python-dev\
    && mkdir -p /var/log/supervisor && mkdir -p /opt/backend/static\
    && pip install --no-cache-dir -r /opt/backend/requirements.txt\
    && python -m nltk.downloader stopwords
WORKDIR /opt/backend
EXPOSE 8000
CMD ["/usr/bin/supervisord"]
