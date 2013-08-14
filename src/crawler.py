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
CONTROL_YUAN_URL = "http://www.cy.gov.tw/sp.asp?xdURL=./di/edoc/db2.asp&ctNode={0:d}&doQuery=1&cPage={1:d}&edoc_no={2:d}"
EDOC_MAPPING = {910: 1, 911: 2, 912: 3, 913: 4}

def getDomain(url):
    reObj = re.match(r'(http://.+/)', url)
    return reObj.group()

def fetchPage(url):
    if DEBUG and os.path.exists(CAHCE_FILE):
        content = fetchPageFromFile(CAHCE_FILE)
    else:
        content = fetchPageFromURL(url)
    if IS_DUMP_FILE:
        fd = open(CAHCE_FILE, 'w')
        fd.write(content)
        fd.close
    return content

def fetchPageFromURL(url):
    return urllib.urlopen(url).read()

def fetchPageFromFile(file):
    fd = open(file, 'r')
    return fd.read()

def contentDownloader(caseType, year = '', page = 1):
    edoc = EDOC_MAPPING[caseType]
    url = CONTROL_YUAN_URL.format(caseType, page, edoc)

    if year != '':
        url += "&intYear="
        url += year

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

def yearParser(parser, content):
    return parseYearNumber(parser)

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
    item = index % 6
    caseNo = index / 6
    if item == 0:
        caseTable[caseNo] = {"date": content.text}
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

def parseYearNumber(parser):
    items = parser.find_all('form', attrs={'action': 'sp.asp'})[1].find_all(
            'select', attrs={'name': 'intYear'})[0].find_all('option')
    years = []
    for item in items:
        reObj = re.match(r'.*value="(\d+)".*', str(item))
        if reObj == None:
            continue
        years.append(reObj.group(1))
    return years

def parsePageNumber(parser):
    try:
        lastPage = parser.find('div', attrs={'class':'page'}).find_all('a')[-1]['href']
        reObj = re.match(r'.*cPage=(\d+).*', lastPage)
        return int(reObj.group(1))
    except Exception, e:
        return 0

def parseCaseTable(parser):
    cases = parser.find('div', attrs={'class': 'lpTb'}).find_all('td')
    caseNum = len(cases) / 6
    if caseNum == 0:
        return []

    caseTable = [None]*caseNum
    idx = 0
    for case in cases:
        insertCase(caseTable, case, idx)
        idx += 1
    return caseTable

def dumpToJson(table, caseType, year, page):
    fileName = "data_{0:d}_{1:s}_{2:d}.json".format(caseType, year, page)
    fd = codecs.open(os.path.join(DOWNLOAD_FOLDER, fileName), 'w', encoding="utf-8")
    json.dump(table, fd, indent=2, ensure_ascii=False)
    fd.close()
    pass

def crawlerByYear(caseType, year):
    print "Download case: {0:d}, year: {1:s}, page: {2:d}".format(caseType, year, 1)
    content = contentDownloader(caseType, year)
    parser = createParser(content)
    pageNum = pageParser(parser, content)
    table = caseParser(parser, content)
    if len(table) > 0:
        dumpToJson(table, caseType, year, 1)

    for idx in xrange(2, pageNum + 1):
        print "Download case: {0:d}, year: {1:s}, page: {2:d}".format(caseType, year, idx)
        content = contentDownloader(caseType, year, idx)
        parser = createParser(content)
        table = caseParser(parser, content)
        if len(table) > 0:
            dumpToJson(table, caseType, year, idx)

    pass

def crawlerByType(caseType):
    # First time
    #print "Download page: {0:d}".format(idx)
    content = contentDownloader(caseType)
    parser = createParser(content)
    years = yearParser(parser, content)

    for year in years:
        crawlerByYear(caseType, year)

    pass

def main(argv):
    crawlerByType(910)
    crawlerByType(911)
    crawlerByType(912)
    crawlerByType(913)
    pass

if __name__ == '__main__':
    FETCH_DOMAIN = getDomain(FETCH_URL)
    main(sys.argv)
