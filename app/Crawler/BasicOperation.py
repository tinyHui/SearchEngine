from time import sleep as sleepSecond
from config import HEADER, OKBLUE, OKGREEN, FAIL, WARNING, ENDC
import os

# SYS
def sleep(seconds):
    sleepSecond(seconds/1000.)


# print message
def printState(*, hint=None, msg=None):
    print(HEADER, hint, ENDC, msg)

def printSuccess(*, hint=None, msg=None):
    print(OKGREEN, hint, ENDC, msg)

def printFail(*, hint=None, msg=None):
    print(FAIL, hint, ENDC, msg)

# files
def save(*, data, filename, dir=None):
    if dir is not None:
        filename = os.path.join(dir, filename)

    if data is None or filename is None:
        return

    try:
        with open(filename, 'wb') as f:
            f.write(data)
    except FileNotFoundError as e:
        dir = os.path.split(filename)[0]
        printFail(hint='Try create folder', msg=dir)
        os.mkdir(dir)
        with open(filename, 'wb') as f:
            f.write(data)


# HTTP connection
def isNormalConn(status):
    if status != 200 and status/100 != 3:
        return False
    return True

def getFileNameInURL(url):
    if url[0] == '/':
        url = url[1:]

    if url is None or url == '':
        url = 'index.html'

    return url