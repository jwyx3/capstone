# credit: http://blog.csdn.net/Bone_ACE/article/details/53306629
from scrapy.utils.reqser import _find_method
from scrapy_redis.queue import Base
from scrapy.core.engine import Request


class SimpleQueue(Base):

    def __len__(self):
        """Return the length of the queue"""
        return self.server.llen(self.key)

    def push(self, request):
        """Push a request"""
        url = request.url
        cb = request.callback or self.spider.parse
        if callable(cb):
            cb = _find_method(self.spider, cb)
            data = '%s--%s' % (cb, url)
            self.server.lpush(self.key, data)

    def pop(self, timeout=0):
        """Pop a request"""
        if timeout > 0:
            data = self.server.brpop(self.key, timeout=timeout)
            if isinstance(data, tuple):
                data = data[1]
        else:
            data = self.server.rpop(self.key)
        if data:
            cb, url = data.split('--', 1)
            try:
                cb = getattr(self.spider, str(cb))
                return Request(url=url, callback=cb)
            except AttributeError:
                raise ValueError("Method %r not found in: %s" % (cb, self.spider))
