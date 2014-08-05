from BasicOperation import sleep, printState, printSuccess, printFail, isNormalConn, save, getFileInURL
from config import DOWNLOAD_DIR, DOWNLOAD_RESULT, URL_DOWNLOAD_LIST, URL_VISITED_LIST, URL_VISITED_FILE_LIST, REDOWNLOAD_TIME, URL_NEW_DOWNLOAD_TIMEOUT, LINK_REF_ACCUM_SEM, DATABASE
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
    def __init__(self, *, interval=100, thread_num=None):
        super(Downloader, self).__init__()
        self.thread_num = thread_num + 1
        self.thread_stop = False
        self.interval = interval
        self.url = None
        self.fail_time = 0          # time of download webpage fail
        self.sql_conn = None
        self.sql_cursor = None

    def run(self):
        printSuccess(hint="Download Thread-%d created." % (self.thread_num))
        
        while not self.thread_stop:
            try:
                (link_name, self.url) = URL_DOWNLOAD_LIST.get(timeout=URL_NEW_DOWNLOAD_TIMEOUT)
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
        (filename, filetype) = getFileInURL(parse_url.path)

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
        # is not a HTML page
        if r.headers['Content-Type'].split(';')[0] != 'text/html':
            return DOWNLOAD_RESULT['SUCCESS']

        if isNormalConn(r.status):
            try:
                file_name = save(data=r.data,filename=filename, dir=DOWNLOAD_DIR)
            except AttributeError as e:
                printFail(hint="Save file fail in", msg=self.url)
                return DOWNLOAD_RESULT['FAIL']
            URL_VISITED_FILE_LIST.put(file_name)

        URL_VISITED_LIST.append(self.url)
        printSuccess(hint="Finish", msg=self.url)

        URL_DOWNLOAD_LIST.put(self.url)
        ##################### End  Save #####################


        ##################### Record Visited Link #####################
        # add to the list
        self.sql_conn = sqlite3.connect(DATABASE)
        self.sql_cursor = self.sql_conn.cursor()

        # insert link address into visited history
        self.sql_cursor.execute("insert into `Pages_linklist` (`title`, `address`) values( '%s', '%s')"
            % (link_name, self.url))
        self.sql_conn.commit()

        # accumulation is a critical section
        LINK_REF_ACCUM_SEM.acquire()            # stop

        # accum the link ref time
        id = self.sql_cursor.execute("select `id` from `Pages_linklist` where `address`='%s'"
            % (self.url)).fetchone()[0]
        accum = self.sql_cursor.execute("select `accum` from `Pages_linkreftime` where `link_id`=%d"
            % (id)).fetchone()
        if accum is None:
            accum = 1
        else:
            accum = accum[0] + 1
        self.sql_cursor.execute("insert into `Pages_linkreftime` (`link_id`, `accum`) values(%d, %d)"
            % (id, accum))        

        self.sql_conn.commit()

        LINK_REF_ACCUM_SEM.release()            # resume

        self.sql_conn.close()
        ##################### End Record #####################

        self.url = None
        self.fail_time = 0
        return DOWNLOAD_RESULT['SUCCESS']
