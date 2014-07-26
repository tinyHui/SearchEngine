from config import HEADER, OKBLUE, OKGREEN, FAIL, WARNING, ENDC, HTTP_RESPONSE_ERROR, LOG_FILE
from urllib3.util.url import parse_url as parseURL
from urllib.parse import urljoin
from time import sleep as sleepSecond
import os

# SYS
def sleep(seconds):
    sleepSecond(seconds/1000.)


# print message
def printState(*, hint='', msg=''):
    logRecord("State\t", hint, msg)
    print(HEADER, hint, ENDC, msg)

def printSuccess(*, hint='', msg=''):
    logRecord("Success\t", hint, msg)
    print(OKGREEN, hint, ENDC, msg)

def printFail(*, hint='', msg=''):
    logRecord("Fail\t", hint, msg)
    print(FAIL, hint, ENDC, msg)

def logRecord(state, hint, msg):
    with open(LOG_FILE, 'a') as f:
        if msg == '':
            f.write("%s%s\n" % (state, hint))
        else:
            f.write("%s%s: %s\n" % (state, hint, msg))
    f.close()

# files
def save(*, data, filename, dir=None):
    if dir is not None:
        filename = os.path.join(dir, filename)

    try:
        with open(filename, 'wb') as f:
            f.write(data)
    except FileNotFoundError as e:
        dir = os.path.dirname(filename)
        printFail(hint='Try create folder', msg=dir)
        os.makedirs(dir)
        with open(filename, 'wb') as f:
            f.write(data)
    f.close()
    return filename

def read(filename):
    if not os.path.isfile(filename):
        return None
    with open(filename, 'r') as f:
        content = f.read()
    return content


# HTTP connection
def isNormalConn(status):
    if status != 200 and status/100 != 3:
        try:
            printFail(hint="Connection Fail", msg=HTTP_RESPONSE_ERROR[status])
        except KeyError as e:
            printFail(hint="Connection Fail", msg=e)
        return False
    return True

def getFileNameInURL(url):
    if url[-1] == '/':
        name = 'index.html'

    return name

def getBaseURL(url):
    try:
        parse_url = parseURL(url)
        url = parse_url.scheme + '://' + parse_url.host
        url = urljoin(url, '/blogs/')
        return url
    except TypeError as e:
        printFail(hint="None Type", msg="url is %s" % url)
        return ""
