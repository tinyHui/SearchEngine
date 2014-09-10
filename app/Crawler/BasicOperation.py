from config import HEADER, OKBLUE, OKGREEN, FAIL, WARNING, ENDC, HTTP_RESPONSE_ERROR, LOG_FILE
from urllib3.util.url import parse_url as parseURL
from urllib.parse import urljoin
from time import sleep as sleepSecond
import os
import re

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


# HTTP connection
def isNormalConn(status):
    if status != 200 and status/100 != 3:
        try:
            printFail(hint="Connection Fail", msg=HTTP_RESPONSE_ERROR[status])
        except KeyError as e:
            printFail(hint="Connection Fail", msg=e)
        return False
    return True

def getFileInURL(url):
    urls = parseURL(url).path.split('/')
    urls = list(filter(lambda x: x!='', urls))  # remove '' items
    try:
        url = urls[-1]
    except IndexError as e:
        # domain only
        return ('index.html', 'html')
    pattern = r'^([\W\w]+)\.([\W\w]+)$'
    m = re.match(pattern, url)
    if m:
        # file full name and file ext name
        return (m.groups(0), m.groups(2))
    else:
        url = '/'.join(urls)
        return (url + '/' + 'index.html', 'html')

def getBaseURL(url):
    try:
        parse_url = parseURL(url)
        url = parse_url.scheme + '://' + parse_url.host
        return url
    except TypeError as e:
        printFail(hint="None Type", msg="url is %s" % url)
        return ""

def genFullURL(base_url, url):
    pattern = r'^\/?([\W\w]*)\/?#[\W\w]*?$'
    m = re.match(pattern, url)
    url = urljoin(base_url, url)
    return url

def isValuableURL(url):
    pattern = r'(^#[\W\w]*$)|(^mailto:[\W\w]*$)|(^news:[\W\w]*$)|(^javascript:[\W\w]*;?$)|(^\/$)'
    m = re.match(pattern, url)
    return not m
