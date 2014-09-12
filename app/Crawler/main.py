from Downloader import Downloader
from config import URL_DOWNLOAD_LIST, URL_VISITED_LIST, DOWLOAD_THREAD_POOL_SIZE, ANAYLIZER_THREAD_POOL_SIZE, DATABASE
from BasicOperation import getBaseURL
from HTMLAnaylizer.LinkExtractor import LinkExtractor
import sqlite3

if __name__ == '__main__':
    ##################### init #####################
    start_url = "https://tinyhui.github.io/"
    base_url = getBaseURL(start_url)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # find any undownloaded pages
    links = cursor.execute("select `title`, `url` from `Pages_linklist` where `content` is NULL or `content`=''").fetchall()
    if len(links) == 0:
        URL_DOWNLOAD_LIST.put(("Main Page", start_url))
    else:
        for title, url in links:
            URL_DOWNLOAD_LIST.put((title, url))

    conn.close()
    ##################### End #####################

    ##################### create threads #####################
    thread_pool_download = []
    thread_pool_link_extract = []
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
