from BasicOperation import sleep, printState, printSuccess, printFail, isNormalConn, save, getFileNameInURL
from config import DOWNLOAD_DIR
from threading import Thread
from urllib3.util.timeout import Timeout
from urllib3.util.url import parse_url as parseURL
from urllib3 import PoolManager
from urllib3.exceptions import SSLError
import certifi

class Downloader(Thread):
    """docstring for Downloader"""
    def __init__(self, *, url=None, interval=10):
        super(Downloader, self).__init__()
        self.thread_stop = False
        self.interval = interval
        self.url = url
        self.fail_time = 0

    def run(self):
        while not self.thread_stop:
            self.download()

            while self.url is None:
                if self.fail_time > 100:
                    self.stop()
                    break

                sleep(self.interval * (self.fail_time+1))
                self.fail_time += 1


    def stop(self):
        self.url = ''
        self.thread_stop = True

    def setURL(self, url):
        self.url = url

    def download(self):
        if self.url is None or self.url == '':
            return

        printState(hint='Connecting', msg=self.url)


        parse_url = parseURL(self.url)
        scheme = parse_url.scheme
        filename = getFileNameInURL(parse_url.path)

        timeout = Timeout(connect=2., read=7.)
        if scheme.lower() is 'https':
            http = PoolManager(
                cert_reqs='CERT_REQUIRED', 
                ca_certs=certifi.where(),
                timeout=timeout, 
            )
        else:
            http = PoolManager(timeout=timeout)

        try:
            r = http.request('GET', self.url)
        except SSLError as e:
            printFail(hint='SSL Error', msg=self.url)

        printState(hint='Establish', msg=self.url)

        if isNormalConn(r.status):
            save(data=r.data,filename=filename, dir=DOWNLOAD_DIR)

        printSuccess(hint='Finish', msg=self.url)
        self.url = None
        self.fail_time = 0


