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