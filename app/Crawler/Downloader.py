from BasicOperation import sleep, printState, printSuccess, printWarning, printFail, isNormalConn
from config import DOWNLOAD_RESULT, URL_DOWNLOAD_LIST, URL_VISITED_LIST, REDOWNLOAD_TIME, URL_NEW_DOWNLOAD_TIMEOUT, DATABASE, DATABASE_LOCK
from threading import Thread
from urllib3.util.timeout import Timeout
from urllib3.util.url import parse_url as parseURL
from urllib3 import PoolManager
from urllib3.exceptions import SSLError, MaxRetryError
from queue import Empty as QueueEmpty
import sqlite3
import certifi

class Downloader(Thread):
    """docstring for Downloader"""
    def __init__(self, *, interval=500, thread_num=None):
        super(Downloader, self).__init__()
        self.thread_num = thread_num + 1
        self.thread_stop = False
        self.interval = interval
        self.title = None
        self.url = None
        self.sql_conn = None
        self.sql_cursor = None

    def run(self):
        printSuccess(hint="Download Thread-%d created." % (self.thread_num))
        self.sql_conn = sqlite3.connect(DATABASE)
        self.sql_cursor = self.sql_conn.cursor()
        
        while True:
            try:
                (self.title, self.url) = URL_DOWNLOAD_LIST.get(timeout=URL_NEW_DOWNLOAD_TIMEOUT)
            except QueueEmpty as e:
                break

            download_result = DOWNLOAD_RESULT['FAIL']
            fail_time = 0            # allowed times for fail download

            # download fail, retry
            while download_result == DOWNLOAD_RESULT['FAIL']:
                # if retry too much times, stop
                if fail_time > REDOWNLOAD_TIME:     break
                # wait a while then retry donwload
                sleep(self.interval * (fail_time+1))
                # begin download
                download_result = self.download()
                fail_time += 1

            if download_result == DOWNLOAD_RESULT['FAIL']:
                printFail(hint="Give up", msg=self.url)
            else:
                URL_VISITED_LIST.put(self.url)
            fail_time = 0
            self.title = None
            self.url = None

        self.sql_conn.close()
        printSuccess(hint="Thread-%d Destoried cause of No URL left." % (self.thread_num))


    def download(self):
        if self.url is None or self.url == '':
            return DOWNLOAD_RESULT['FAIL']

        ##################### Start Download Web Page #####################
        printState(hint="Connecting", msg=self.url)
        parse_url = parseURL(self.url)
        scheme = parse_url.scheme

        headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36"}
        timeout = Timeout(connect=2., read=7.)
        if scheme.lower() is 'https':
            http = PoolManager(
                cert_reqs='CERT_REQUIRED', 
                ca_certs=certifi.where(),
                headers=headers,
                timeout=timeout
            )
        else:
            http = PoolManager(headers=headers, timeout=timeout)

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
        # is not a HTML page
        if r.headers['Content-Type'].split(';')[0] != 'text/html':
            printWarning(hint="Not a Web Page", msg=self.url)
            return DOWNLOAD_RESULT['SUCCESS']

        (connected, message) = isNormalConn(r.status)
        if connected:
            if self.sql_cursor.execute('''select count(1) from `Pages_linklist` where `url`=?''',
                (self.url,)).fetchone()[0] == 0:
                DATABASE_LOCK.acquire()
                self.sql_cursor.execute('''insert into `Pages_linklist` 
                        (`title`, `url`) values(?, ?)''', 
                        (self.title, self.url))
                DATABASE_LOCK.release()
                printWarning(hint="Create db record while downloading", msg=self.url)
            # update content 
            self.sql_cursor.execute('''update `Pages_linklist` 
                set `content`=? where `url`=?''', 
                (r.data, self.url))

            DATABASE_LOCK.acquire() 
            self.sql_conn.commit()
            DATABASE_LOCK.release()
            printSuccess(hint="Saved", msg=self.url)
            return DOWNLOAD_RESULT['SUCCESS']
        else:
            printFail(hint=message, msg=self.url)
            return DOWNLOAD_RESULT['FAIL']
        ##################### End  Save #####################