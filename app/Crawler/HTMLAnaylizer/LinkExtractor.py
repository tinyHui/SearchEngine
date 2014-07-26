from config import URL_DOWNLOAD_LIST, URL_VISITED_FILE_LIST, URL_NEW_EXTRACT_TIMEOUT
from BasicOperation import printSuccess, printFail, read, getBaseURL
from bs4 import BeautifulSoup
from threading import Thread
from queue import Empty as QueueEmpty
from urllib.parse import urljoin

class LinkExtractor(Thread):
    """docstring for LinkExtractor"""
    def __init__(self, *, base_url):
        super(LinkExtractor, self).__init__()
        self.base_url = base_url
        self.html_file = None
        self.soup = None

    def run(self):
        while True:
            try:
                # self.html_file = URL_VISITED_FILE_LIST.get(timeout=URL_NEW_EXTRACT_TIMEOUT)
                self.html_file = URL_VISITED_FILE_LIST.get(timeout=10)      # time unit is second
            except QueueEmpty as e:
                printSuccess(hint="Link Extractor Destoried cause of No More File need to be anaylises.")
                return

            content = read(self.html_file)
            try:
                self.soup = BeautifulSoup(content)
            except TypeError as e:
                printFail(hint="Unable to open", msg=self.html_file)
                continue

            for link_tag in self.soup.find_all('a'):
                link = link_tag.get('href')
                if link[0] == '/':
                    link = urljoin(self.base_url, link)

                if link[0] != "#" and \
                   link != "javascript:;":
                   link_base_url = getBaseURL(link)
                   if link_base_url == self.base_url:
                        URL_DOWNLOAD_LIST.put(link)
