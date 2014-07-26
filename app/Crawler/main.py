from Downloader import Downloader
from time import sleep
from config import URL_LIST, THREAD_POOL_SIZE

if __name__ == '__main__':
    start_url = "https://www.python.org3/"
    URL_LIST.put(start_url)

    # begin start multi threads
    thread_pool_download = []
    for i in range(THREAD_POOL_SIZE):
        new_thread_download = Downloader(thread_num=i)
        new_thread_download.start()
        thread_pool_download.append(new_thread_download)
