from config import URL_DOWNLOAD_LIST, URL_VISITED_FILE_LIST, URL_NEW_EXTRACT_TIMEOUT, DATABASE
from BasicOperation import printState, printSuccess, printFail, read, getBaseURL, genFullURL, isValuableURL
from bs4 import BeautifulSoup
from threading import Thread
from queue import Empty as QueueEmpty
import sqlite3

class LinkExtractor(Thread):
    """docstring for LinkExtractor"""
    def __init__(self, *, base_url):
        super(LinkExtractor, self).__init__()
        self.base_url = base_url
        self.html_file = None
        self.soup = None
        self.sql_conn = None
        self.sql_cursor = None

    def run(self):
        while True:
            try:
                # self.html_file = URL_VISITED_FILE_LIST.get(timeout=URL_NEW_EXTRACT_TIMEOUT)
                self.html_file = URL_VISITED_FILE_LIST.get(timeout=10)      # time unit is second
            except QueueEmpty as e:
                printSuccess(hint="Link Extractor Destroyed cause of No More File need to be anaylises.")
                return

            content = read(self.html_file)
            try:
                self.soup = BeautifulSoup(content)
            except TypeError as e:
                printFail(hint="Unable to open", msg=self.html_file)
                continue

            self.sql_conn = sqlite3.connect(DATABASE)
            self.sql_cursor = self.sql_conn.cursor()

            for link_tag in self.soup.find_all('a'):
                link_name = link_tag.text.replace('\n','').strip()
                link_addr = link_tag.get('href').strip()

                # link is None or empty string
                if link_addr is None or link_addr == "":
                    continue

                # if link is not a valuable link
                if not isValuableURL(link_addr):
                    continue
                
                # full fill the link as a 
                link_addr = genFullURL(self.base_url, link_addr)
                
                # if link is not under the same domain
                if not self.base_url == getBaseURL(link_addr):
                    continue

                # have never been downloaded
                sql_reg = self.sql_cursor.execute("select count(*) from `Pages_linklist` where `address`='%s'"
                    % (link_addr))

                # if this URL is been scanned before
                sql_result = sql_reg.fetchone()
                if not sql_result[0] == 0:
                    continue

                # add to the list
                URL_DOWNLOAD_LIST.put(link_addr)
                # insert into database
                self.sql_cursor.execute("insert into `Pages_linklist` (`title`, `address`) values( '%s', '%s')"
                    % (link_name, link_addr))
        
            self.sql_conn.commit()
            self.sql_conn.close()