# credit: https://stackoverflow.com/questions/21839676/how-to-write-a-downloadhandler-for-scrapy-that-makes-requests-through-socksipy

from scrapy.core.downloader.handlers.http11 import HTTP11DownloadHandler, ScrapyAgent
from scrapy.core.downloader.webclient import _parse
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from txsocksx.http import SOCKS5Agent
import base64


class TorScrapyAgent(ScrapyAgent):
    _Agent = SOCKS5Agent

    def _get_agent(self, request, timeout):
        proxy = request.meta.get('proxy')
        if proxy:
            proxy_scheme, _, proxy_host, proxy_port, _ = _parse(proxy)
            if proxy_scheme == 'socks5':
                methods = {'anonymous': ()}
                basic_auth_header = request.headers.get('Proxy-Authorization', None)
                if basic_auth_header:
                    user_pass = base64.b64decode(basic_auth_header.strip().split()[1])
                    username, password = user_pass.split(':')
                    methods = {'login': (username, password)}
                endpoint = TCP4ClientEndpoint(reactor, proxy_host, proxy_port)
                return self._Agent(reactor, proxyEndpoint=endpoint, endpointArgs=dict(methods=methods))
        return super(TorScrapyAgent, self)._get_agent(request, timeout)


class TorHTTPDownloadHandler(HTTP11DownloadHandler):
    def download_request(self, request, spider):
        agent = TorScrapyAgent(contextFactory=self._contextFactory, pool=self._pool,
                               maxsize=getattr(spider, 'download_maxsize', self._default_maxsize),
                               warnsize=getattr(spider, 'download_warnsize', self._default_warnsize))
        return agent.download_request(request)
