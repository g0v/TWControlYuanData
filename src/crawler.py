# encoding: utf-8
import os
import re
import sys
import urllib
import json
import codecs
try:
    import lxml
    from bs4 import BeautifulSoup
except Exception, e:
    print "Please install package BeautifulSoup and lxml."
    exit()


default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


DEBUG = True
IS_DUMP_FILE = False
CAHCE_FILE = "./dump.log"
FETCH_URL = 'http://www.cy.gov.tw/sp.asp?xdUrl=.%2FDI%2Fedoc%2Fdb2.asp&ctNode=911&edoc_no=2&doQuery=1&intYear=&mm=&input_edoc_no=&case_pty=&input_edoc_unit=&keyword=&submit=%E6%9F%A5%E8%A9%A2'
DOWNLOAD_FOLDER = '../data/'

def getDomain(url):
    reObj = re.match(r'(http://.+/)',url)
    return reObj.group()

def fetchPage(url):
    
    if DEBUG and os.path.exists(CAHCE_FILE):
        content = fetchPageFromFile(CAHCE_FILE)
    else:
        content = fetchPageFromURL(url)
    if IS_DUMP_FILE:
        fd = open(CAHCE_FILE,'w')
        fd.write(content)
        fd.close
    return content

def fetchPageFromURL(url):
    return urllib.urlopen(url).read()

def fetchPageFromFile(file):
    fd = open(file,'r')
    return fd.read()

def contentDownloader(url):
    pass

def contentParser(content):
    soup = BeautifulSoup(content)
    talbe = parseCaseTable(soup)
    return talbe

def normalizeContent(content):
    content = content.encode('utf-8')
    content = content.replace(' ', '')
    content = content.replace('\t', '')
    content = content.replace('\n', '')
    content = content.replace('\r', '')
    return content

def insertCase(caseTable, content, index):
    item = index%6
    caseNo = index/6
    if item == 0:
        caseTable[caseNo] = {"date":content.text}
        pass
    elif item == 1:
        caseTable[caseNo]['id'] = normalizeContent(content.text)
        pass
    elif item == 2: 
        caseTable[caseNo]['describe'] = normalizeContent(content.text)
        pass
    elif item == 3:
        caseTable[caseNo]['docx'] = FETCH_DOMAIN + normalizeContent(content.a['href'])
        pass
    elif item == 4:
        caseTable[caseNo]['pdf'] = ''
        pass
    elif item == 5:
        caseTable[caseNo]['reportLink'] = FETCH_DOMAIN + normalizeContent(content.a['href'])
        pass
    pass

def parseCaseTable(parser):
    cases = parser.find('div',attrs={'class':'lpTb'}).find_all('td')
    caseNum = len(cases)/6
    caseTable = [None]*caseNum
    idx = 0
    for case in cases:
        insertCase(caseTable, case, idx)
        idx += 1
    return caseTable

def dumpToJson(table):
    fd = codecs.open(os.path.join(DOWNLOAD_FOLDER,'data.json'),'w',encoding="utf-8")
    json.dump(table,fd,indent=2,ensure_ascii=False)
    fd.close()
    pass

def main(argv):
    content = fetchPage(FETCH_URL)
    table = contentParser(content)
    dumpToJson(table)
    pass

if __name__ == '__main__':
    FETCH_DOMAIN = getDomain(FETCH_URL)
    main(sys.argv)
