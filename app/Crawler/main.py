from Downloader import Downloader
from time import sleep

if __name__ == '__main__':
    new_thread = Downloader(url='https://www.python.org/')
    new_thread.start()
