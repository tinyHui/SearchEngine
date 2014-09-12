from config import URL_DOWNLOAD_LIST, URL_VISITED_LIST, URL_NEW_EXTRACT_TIMEOUT, DATABASE, URL_NEW_EXTRACT_TIMEOUT, DATABASE_LOCK
from BasicOperation import printSuccess, printFail, getBaseURL, genFullURL
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
                DATABASE_LOCK.acquire() 
                self.sql_conn.commit()
                DATABASE_LOCK.release()
                break

            try:
                self.soup = BeautifulSoup(content)
            except TypeError as e:
                printFail(hint="Unable to open", msg=self.url)
                continue

            sublinks = self.extractAllLinks()
            sublinks_num = 0

            for (title, addr)  in sublinks:
                # full fill the link as a 
                addr = genFullURL(self.base_url, addr)
                # if link is not a valuable link
                if addr is None:
                    continue

                try:
                    self.sql_cursor.execute('''insert into `Pages_linklist` 
                        (`title`, `url`) values (?, ?)''', 
                        (title, addr))
                    self.sql_cursor.execute('''insert into  `Pages_sublinklist` (`link_id`, `sublink_id`) 
                        select a.`id`, b.`id` from `Pages_linklist` a, `Pages_linklist` b 
                        where a.`url`=? and b.`url`=?''',
                        (self.url, addr))
                    URL_DOWNLOAD_LIST.put((title, addr))
                except sqlite3.IntegrityError as e:         # if recorded before
                    pass
                sublinks_num += 1

            self.sql_cursor.execute('''update `Pages_linklist` 
                set `sublinks_num`=? where `url`=?''', 
                (sublinks_num, self.url))

            printSuccess(hint="Extract all links under", msg=self.url)

            DATABASE_LOCK.acquire() 
            self.sql_conn.commit()
            DATABASE_LOCK.release()

        self.sql_conn.close()


    def extractAllLinks(self):
        tags = self.soup.find_all('a')
        links = []
        for tag in tags:
            try:
                title = tag.text.replace('\n','').strip()
                addr = tag.get('href').strip()
                links.append((title,addr))
            except AttributeError as e:
                continue
        
        return links
