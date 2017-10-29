import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
sys.path.append('/usr/local/lib/python3.6/site-packages')
import redis
from seeds import seeds_dict

r = redis.StrictRedis(host='redis', port=6379, db=0)

print("start to feed crawler")
for key, start_urls in seeds_dict.items():
    print("sadd {}: {}".format(key, start_urls))
    for url in start_urls:
        r.sadd(key, url)
print("finish")
