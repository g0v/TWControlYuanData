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


DEBUG = False
IS_DUMP_FILE = False
CAHCE_FILE = "./dump.log"
FETCH_URL = 'http://www.cy.gov.tw/sp.asp?xdUrl=.%2FDI%2Fedoc%2Fdb2.asp&ctNode=911&edoc_no=2&doQuery=1&intYear=&mm=&input_edoc_no=&case_pty=&input_edoc_unit=&keyword=&submit=%E6%9F%A5%E8%A9%A2'
DOWNLOAD_FOLDER = '../data/'
DOCUMENT_FOLDER = '../data/doc'

CONTROL_YUAN_URL = "http://www.cy.gov.tw/sp.asp?xdURL=./di/edoc/db2.asp&ctNode={0:d}&doQuery=1&cPage={1:d}&edoc_no=2&intYear="

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

def contentDownloader(caseType, page):
    url = CONTROL_YUAN_URL.format(caseType,page)
    content = fetchPage(url)
    return content

def createParser(content):
    return BeautifulSoup(content)

def caseParser(parser, content):
    talbe = parseCaseTable(parser)
    return talbe

def pageParser(parser, content):
    pageNum = parsePageNumber(parser)
    return pageNum

def page():
    pass

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
        try:
            caseTable[caseNo]['docx'] = FETCH_DOMAIN + normalizeContent(content.a['href'])
        except:
            caseTable[caseNo]['docx'] = ''
    elif item == 4:
        try:
            caseTable[caseNo]['pdf'] = FETCH_DOMAIN + normalizeContent(content.a['href'])
        except:
            caseTable[caseNo]['pdf'] = ''
    elif item == 5:
        try:
            caseTable[caseNo]['reportLink'] = FETCH_DOMAIN + normalizeContent(content.a['href'])
        except Exception, e:
            caseTable[caseNo]['reportLink'] = ''
    pass

def parsePageNumber(parser):
    try:
        lastPage = parser.find('div',attrs={'class':'page'}).find_all('a')[-1]['href']
        reObj = re.match(r'.*cPage=(\d+).*',lastPage)
        return int(reObj.group(1))
    except Exception, e:
        return 0


def parseCaseTable(parser):
    cases = parser.find('div',attrs={'class':'lpTb'}).find_all('td')
    caseNum = len(cases)/6
    caseTable = [None]*caseNum
    idx = 0
    for case in cases:
        insertCase(caseTable, case, idx)
        idx += 1
    return caseTable

def dumpToJson(table,caseType,page):
    fileName = "data_{0:d}_{1:d}.json".format(caseType,page)
    fd = codecs.open(os.path.join(DOWNLOAD_FOLDER,fileName),'w',encoding="utf-8")
    json.dump(table,fd,indent=2,ensure_ascii=False)
    fd.close()
    pass

def crawlerByType(caseType):
    idx = 1

    # First time
    print "Download page: {0:d}".format(idx)
    content = contentDownloader(caseType,idx)
    parser = createParser(content)
    pageNum = pageParser(parser,content)
    table = caseParser(parser, content)
    dumpToJson(table,caseType,idx)

    for idx in xrange(2,pageNum+1):
        print "Download page: {0:d}".format(idx)
        content = contentDownloader(caseType,idx)
        parser = createParser(content)
        table = caseParser(parser, content)
        dumpToJson(table,caseType,idx)
    pass

def main(argv):
    crawlerByType(911)
    pass

if __name__ == '__main__':
    FETCH_DOMAIN = getDomain(FETCH_URL)
    main(sys.argv)
