from Downloader import Downloader
from config import URL_DOWNLOAD_LIST, URL_VISITED_FILE_LIST, DOWLOAD_THREAD_POOL_SIZE
from BasicOperation import getBaseURL
from HTMLAnaylizer.LinkExtractor import LinkExtractor
from time import sleep

if __name__ == '__main__':
    start_url = "https://www.python.org/"
    base_url = getBaseURL(start_url)
    
    # begin start multi threads
    URL_DOWNLOAD_LIST.put(start_url)
    thread_pool_download = []
    for i in range(DOWLOAD_THREAD_POOL_SIZE):
        new_thread_download = Downloader(thread_num=i)
        thread_pool_download.append(new_thread_download)
    
    for i in range(DOWLOAD_THREAD_POOL_SIZE):
        thread_pool_download[i].start()

    thread_link_extract = LinkExtractor(base_url=base_url)
    thread_link_extract.start()
