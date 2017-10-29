# credit: http://blog.csdn.net/bone_ace/article/details/53107018
from scrapy_redis.dupefilter import RFPDupeFilter
from hashlib import sha1


def get_hash(cap, seed):
    def hash(value):
        ret = 0
        for i in range(len(value)):
            ret += seed * ret + ord(value[i])
        return (cap - 1) & ret
    return hash


class BloomFilter(object):
    def __init__(self, server, key, size=28):
        self.server = server
        self.key = key
        self.bit_size = 1 << size  # 32M
        self.seeds = [5, 7, 11, 13, 31, 37, 61]
        self.hash_func = [get_hash(self.bit_size, seed) for seed in self.seeds]

    @staticmethod
    def __encode(item):
        x_sha1 = sha1()
        x_sha1.update(item)
        return x_sha1.hexdigest()

    def __contains__(self, item):
        if not item:
            return False
        s = self.__encode(item)
        name = self.key
        return all(self.server.getbit(name, f(s)) for f in self.hash_func)

    def add(self, item):
        if not item:
            return
        s = self.__encode(item)
        name = self.key
        for f in self.hash_func:
            self.server.setbit(name, f(s), 1)


class BFDupeFilter(RFPDupeFilter):
    def __init__(self, server, key, debug=False):
        """Initialize the duplicates filter.

        Parameters
        ----------
        server : redis.StrictRedis
            The redis server instance.
        key : str
            Redis key Where to store fingerprints.
        debug : bool, optional
            Whether to log filtered requests.

        """
        self.server = server
        self.key = key
        self.debug = debug
        self.logdupes = True
        self.bf = BloomFilter(server, key)

    def request_seen(self, request):
        """Returns True if request was already seen.

        Parameters
        ----------
        request : scrapy.http.Request

        Returns
        -------
        bool

        """
        fp = self.request_fingerprint(request)
        # This returns the number of values added, zero if already exists.
        #added = self.server.sadd(self.key, fp)
        #return added == 0

        # use bloom filter
        if fp in self.bf:
            return True
        else:
            self.bf.add(fp)
            return False
