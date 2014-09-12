from config import HEADER, OKBLUE, OKGREEN, FAIL, WARNING, ENDC, HTTP_RESPONSE_ERROR, LOG_FILE
from urllib3.util.url import parse_url as parseURL
from urllib.parse import urljoin
from time import sleep as sleepSecond
import mimetypes as mime
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

def printWarning(*, hint='', msg=''):
    logRecord("Warning\t", hint, msg)
    print(WARNING, hint, ENDC, msg)

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
            return (False, HTTP_RESPONSE_ERROR[status])
        except KeyError as e:
            return (False, e)
    return (True, "Success")


def getBaseURL(url):
    try:
        parse_url = parseURL(url)
        url = parse_url.scheme + '://' + parse_url.host
        return url
    except TypeError as e:
        printFail(hint="None Type", msg="url is %s" % url)
        return ""


def genFullURL(base_url, url):
    # url is valuable
    pattern = r'(^\/?)((#[\W\w]*$)|(mailto:[\W\w]*$)|(news:[\W\w]*$)|(javascript:[\W\w]*;?$))'
    m = re.match(pattern, url)
    if m:
        return None
    
    # under same domine
    url_host = parseURL(url).host
    if not (url_host is None or url_host == base_url):
        return None

    (type, _) = mime.guess_type(url)
    if not (type is None or type == "text/html"):
        return None

    url = urljoin(base_url, url)
    return url
