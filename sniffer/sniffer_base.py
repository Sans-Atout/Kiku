from urllib3 import PoolManager
from time import sleep
from random import randint
from bs4 import BeautifulSoup

# the PoolManager for the request
HTTP_REQUESTER = PoolManager()

#the defaut header use for making website request
HEADERS =   { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

def getSniffer(url,minWait=30,maxWait=60,t=10,p= None):
    """
        Function that executes a GET request and outputs the corresponding
        sniffing tool.

        (param)url      : the get request url
        (param)minWait  : the minimum time to wait before making the request
                          (in second) the default value is 30s
        (param)maxWait  : the maximum time to wait before making the request
                          (in second) the default value is 60s
        (param)t        : the timeout time (in second). the default value is 10s
        (param)p        : the body param of the request. the default value is None

        (return) tupple of value compose of :
                        (boolean)   : does the request succed or not
                        (int)       : the response status (if time the response
                                      status is 0)
                        (bs4)       : the bs4 object
    """
    sleep_random = randint(minWait,maxWait)
    sleep(sleep_random)
    try:
        response = HTTP_REQUESTER.request("GET",url,p,HEADERS,timeout=t)
        if response.status != 200:
            return False, response.status, "Error"
        return True, response.status, BeautifulSoup(response.data, features="lxml")
    except Exception as e:
        return False, 0 , e
