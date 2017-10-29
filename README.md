# capstone1

### install
* [mongodb](https://docs.mongodb.com/v3.0/tutorial/install-mongodb-on-ubuntu/)
* redis-cli: `apt-get install redis-tools`

### configuration
* add `PATH=<workspace>/used_car/used_car/tools:$PATH` to .bashrc

### vim tips
* remove string after last comma: `%s!^\([^,]*,\)\{2\}\zs.*!!g`
* remove last comma: `%s/,$//g`
* remove string after first comma: `%s/[^,]*$//`

### run crawler
* crawl make and model: `scrapy crawl makemodel -t csv -o data/makemodel.csv`
* crawl make and model with start/pause: `scrapy crawl makemodel -t csv -o data/makemodel1.csv -s JOBDIR=crawls/makemodel1`
* scale crawler: `docker-compose scale crawler_sfbay=2`

### issue
* install vega-embed failed: [solution](https://github.com/Automattic/node-canvas/issues/822)

### deployment in production
* `docker stack deploy --compose-file=docker-compose.yml capstone`
* `docker-compose build --no-cache feeder`
* `docker-compose -f docker-compose-prod.yml up -d --build --force-recreate frontend`
* `docker rm $(docker ps -a --format {{.ID}})`
* `docker rmi $(docker images -f "dangling=true" -q)`

### steps to setup

1. git clone
1. run `bash setup.sh`
1. run `bash start.sh`
1. prepare secret files

```
> mkdir /opt/secrets/

create these files:

> ls -l /opt/secrets/
total 28
-rw-r--r-- 1 root root 41 Oct 27 16:39 app-worker-token # token of one user of Django, you can modify this file later
-rw-r--r-- 1 root root 13 Oct 27 16:31 mysql-password # e.g. pass
-rw-r--r-- 1 root root 18 Oct 27 16:31 mysql-root  # e.g. root-pass
-rw-r--r-- 1 root root  7 Oct 27 16:31 mysql-user  # e.g. user1
-rw-r--r-- 1 root root 27 Oct 27 16:32 proxy       # e.g. http://1.1.1.1:xxx
-rw-r--r-- 1 root root 62 Oct 27 16:30 secret-key  # e.g. xojsjsflankndgoaee
-rw-r--r-- 1 root root 18 Oct 28 14:52 static-root # /www/data/static 

```

1. create super user and worker in django

```

login to backend docker and create super user:

> python manage.py createsuperuser

visite http://localhost:8000/admin/

# we use gunicorn to serve the static files of django
# so the admin ui doesn't work
#
# workaround:
# restart backend using DEBUG and development server
# use the admin GUI to create token

login use super user

create one user: worker

assign "ad -create" permission to worker

create tokens for both super user and worker

```

1. load make and model data

```
go to backend/tools, modify token of load_make.py

> python load_make.py
```

1. visit http://localhost:80/ (must keep login status in django, authentication model is bad now!)

### some thought
* not familar with django, so hard to quickly debug. but really feature rich!!
* the config of nginx is so complex for me ..
* need more UI knowledge


