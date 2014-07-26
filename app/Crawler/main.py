from Downloader import Downloader
from time import sleep

if __name__ == '__main__':
    try:
        new_thread = Downloader(url='http://www.nottingham.edu.cn/en/index.aspx')
        new_thread.start()
    except KeyboardInterrupt:
        pass
