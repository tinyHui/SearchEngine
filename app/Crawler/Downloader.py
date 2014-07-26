from BasicOperation import sleep, printState, printSuccess, printFail, isNormalConn, save, getFileNameInURL
from config import DOWNLOAD_DIR, DOWNLOAD_RESULT, URL_LIST, REDOWNLOAD_TIME, URL_INPUT_TIMEOUT
from threading import Thread
from urllib3.util.timeout import Timeout
from urllib3.util.url import parse_url as parseURL
from urllib3 import PoolManager
from urllib3.exceptions import SSLError, MaxRetryError
from queue import Empty as QueueEmpty
import certifi

class Downloader(Thread):
    """docstring for Downloader"""
    def __init__(self, *, interval=1000, thread_num=None):
        super(Downloader, self).__init__()
        self.thread_num = thread_num + 1
        self.thread_stop = False
        self.interval = interval
        self.url = None
        self.fail_time = 0          # time of download webpage fail

    def run(self):
        printSuccess(hint="Download Thread-%d created." % (self.thread_num))
        
        while not self.thread_stop:
            try:
                self.url = URL_LIST.get(timeout=URL_INPUT_TIMEOUT)
            except QueueEmpty as e:
                printSuccess(hint="Thread-%d Destoried cause of No URL left." % (self.thread_num))
                return

            download_result = self.download()

            # download fail, retry
            while download_result != DOWNLOAD_RESULT:
                # if retry too much times, stop
                if self.fail_time > REDOWNLOAD_TIME:    break
                # wait a while then retry donwload
                sleep(self.interval * (self.fail_time+1))
                self.fail_time += 1
                # redownload
                download_result = self.download()

        printSuccess(hint="Thread-%d Destoried." % (self.thread_num))

    def stop(self):
        self.url = ''
        self.thread_stop = True

    def download(self):
        if self.url is None or self.url == '':
            return DOWNLOAD_RESULT['FAIL']

        ##################### Start Download Web Page #####################
        
        printState(hint="Connecting", msg=self.url)
        parse_url = parseURL(self.url)
        scheme = parse_url.scheme
        filename = getFileNameInURL(parse_url.path)

        timeout = Timeout(connect=2., read=7.)
        if scheme.lower() is 'https':
            http = PoolManager(
                cert_reqs='CERT_REQUIRED', 
                ca_certs=certifi.where(),
                timeout=timeout
            )
        else:
            http = PoolManager(timeout=timeout)

        try:
            r = http.request('GET', self.url)
            printState(hint='Establish', msg=self.url)

        except SSLError as e:
            printFail(hint="SSL Error", msg=self.url)
            return DOWNLOAD_RESULT['FAIL']
        except MaxRetryError as e:
            printFail(hint="Resolve Error", msg=self.url)
            return DOWNLOAD_RESULT['FAIL']

        ##################### End #####################

        ##################### Start Save Web Page #####################

        if isNormalConn(r.status):
            save(data=r.data,filename=filename, dir=DOWNLOAD_DIR)

        printSuccess(hint="Finish", msg=self.url)
        self.url = None
        self.fail_time = 0
        return DOWNLOAD_RESULT['SUCCESS']

        ##################### End #####################
