FROM nginx
ADD nginx.conf /etc/nginx/nginx.conf
RUN set -x\
    && mkdir -p /www/data/\
    && apt-get update && apt-get install -y vim
EXPOSE 80