from Downloader import Downloader
from config import URL_DOWNLOAD_LIST, URL_VISITED_FILE_LIST, DOWLOAD_THREAD_POOL_SIZE, ANAYLIZER_THREAD_POOL_SIZE
from BasicOperation import getBaseURL
from HTMLAnaylizer.LinkExtractor import LinkExtractor
from time import sleep

if __name__ == '__main__':
    start_url = "https://www.python.org/"
    base_url = getBaseURL(start_url)
    
    # begin start multi threads
    URL_DOWNLOAD_LIST.put(start_url)
    thread_pool_download = []
    thread_pool_link_extract = []

    ##################### create threads #####################
    for i in range(DOWLOAD_THREAD_POOL_SIZE):
        new_downloader = Downloader(thread_num=i)
        thread_pool_download.append(new_downloader)

    for i in range(ANAYLIZER_THREAD_POOL_SIZE):
        new_link_extractor = LinkExtractor(base_url=base_url)
        thread_pool_link_extract.append(new_link_extractor)
    ##################### End #####################

    ##################### start threads #####################
    for i in range(DOWLOAD_THREAD_POOL_SIZE):
        thread_pool_download[i].start()

    for i in range(ANAYLIZER_THREAD_POOL_SIZE):
        thread_pool_link_extract[i].start()
    ##################### End #####################
