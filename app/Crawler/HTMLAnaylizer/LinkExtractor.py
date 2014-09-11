from config import URL_DOWNLOAD_LIST, URL_VISITED_LIST, URL_NEW_EXTRACT_TIMEOUT, DATABASE, URL_NEW_EXTRACT_TIMEOUT, LINK_REF_ACCUM_SEM
from BasicOperation import printSuccess, printFail, getBaseURL, genFullURL, isValuableURL
from bs4 import BeautifulSoup
from threading import Thread
from queue import Empty as QueueEmpty
import sqlite3

class LinkExtractor(Thread):
    """docstring for LinkExtractor"""
    def __init__(self, *, base_url):
        super(LinkExtractor, self).__init__()
        self.base_url = base_url
        self.url = None
        self.soup = None
        self.sql_conn = None
        self.sql_cursor = None

    def run(self):
        self.sql_conn = sqlite3.connect(DATABASE)
        self.sql_cursor = self.sql_conn.cursor()

        while True:
            try:
                self.url = URL_VISITED_LIST.get(timeout=URL_NEW_EXTRACT_TIMEOUT)      # time unit is second
            except QueueEmpty as e:
                printSuccess(hint="Link Extractor Destroyed cause of No More File need to be anaylises.")
                return

            try:
                content = self.sql_cursor.execute("select `content` from `Pages_linklist` where `url`=?", 
                    (self.url,)).fetchone()[0]
            except TypeError as e:
                print(self.sql_cursor.execute("select `content` from `Pages_linklist` where `url`=?", 
                    (self.url,)).fetchone())
                break

            try:
                self.soup = BeautifulSoup(content)
            except TypeError as e:
                printFail(hint="Unable to open", msg=self.url)
                continue

            for link_tag in self.soup.find_all('a'):
                try:
                    link_title = link_tag.text.replace('\n','').strip()
                    link_addr = link_tag.get('href').strip()
                except AttributeError as e:
                    continue

                # if link is not a valuable link
                if not isValuableURL(link_addr):
                    continue
         
                # full fill the link as a 
                link_addr = genFullURL(self.base_url, link_addr)
                
                # if link is not under the same domain
                if not self.base_url == getBaseURL(link_addr):
                    continue

                # have never been recorded
                if self.sql_cursor.execute('''select count(1) from `Pages_linklist` where `url`=?''',
                    (link_addr,)).fetchone()[0] == 0:
                    URL_DOWNLOAD_LIST.put((link_title, link_addr))
                    self.accumRefTime(link_title, link_addr, firsttime=True)
                else:
                    self.accumRefTime(link_title, link_addr, firsttime=False)   

            printSuccess(hint="Extract all links under", msg=self.url)
        
        self.sql_conn.commit()
        self.sql_conn.close()

    def accumRefTime(self, link_title, link_addr, firsttime):
        # accumulation is a critical section
        LINK_REF_ACCUM_SEM.acquire()            # stop

        if firsttime:
            self.sql_cursor.execute('''insert into `Pages_linklist` 
                    (`title`, `url`, `reftime`) values(?, ?, ?)''', 
                    (link_title, link_addr, 1))
        else:
            self.sql_cursor.execute('''update `Pages_linklist` set `reftime`=`reftime`+1 where `url`=?''', 
                (self.url,))

        self.sql_conn.commit()

        LINK_REF_ACCUM_SEM.release()            # resume