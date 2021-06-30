# -*- coding: utf-8 -*-


import logging
import requests
import os
import time
from urllib import parse
from pyquery import PyQuery as pq
# 先修改配置
cookieString = "JSESSIONID=xxxx;"
wiki_page_url = "https://xxx.xxx.com.cn/pages/viewpage.action?pageId=xxxx"
wiki_title = "xxx"
dir = "./"+wiki_title


#
# Accept:application/json, text/javascript, */*; q=0.01
# Accept-Encoding:gzip, deflate, sdch
# Accept-Language:en-US,en;q=0.8
# Connection:keep-alive
# User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36 OPR/44.0.2510.857
#
def generateHeaders():
    headersBrower = '''
Accept: application/json, text/javascript, */*; q=0.01
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9,zh-TW;q=0.8,en-US;q=0.7,en;q=0.6
Connection: keep-alive
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36
X-Requested-With: XMLHttpRequest
    '''

    headersMap = dict()
    for item in headersBrower.splitlines():
        item = str.strip(item)
        if item and ":" in item:
            (key, value) = item.split(":", 1)
            headersMap[str.strip(key)] = str.strip(value)

    return headersMap


# 如果wiki需要登录验证,先用浏览器访问wiki,登录以后,获取该用户的cookie信息. cookie信息一般包含JSESSIONID
def genereateCookies():
    cookieMap1 = {}
    for item in cookieString.split(";"):
        item = str.strip(item)
        if item and "=" in item:
            (key, value) = item.split("=", 1)
            cookieMap1[str.strip(key)] = str.strip(value)

    return cookieMap1


def save_file(url, path):
    if os.path.exists(path):
        logging.debug("exist path=" + path)
        return

    logging.debug("将 %s 保存到 %s" % (url, path))

    logging.debug("start get " + url)

    resp = requests.get(url, timeout=300, headers=generateHeaders(), cookies=genereateCookies(), stream=True)

    if resp.status_code == 200:

        with open(path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
            f.close()

        logging.debug("save file " + path)

        time.sleep(3)

    else:
        print("error ", resp.status_code)


def parse_host_pageId_fromurl(url):
    r = parse.urlsplit(url)

    if r.port == None:
        host = r.scheme + "://" + r.netloc
    else:
        host = r.scheme + "://" + r.netloc + ":" + r.port

    params = parse.parse_qs(r.query, True)
    if "pageId" in params:
        pageId = params["pageId"][0]

    if "local-storage" in url:
        pageId = 20505511
    return (host, pageId)


def get_sub_pages_url(parentUrl):
    url = "%s/plugins/pagetree/naturalchildren.action?decorator=none&excerpt=false&sort=position&reverse=false&disableLinks=false&expandCurrent=false&hasRoot=true&pageId=%s&treeId=0&startDepth=0" % parse_host_pageId_fromurl(
        parentUrl)
    resp = requests.get(url, timeout=300, headers=generateHeaders(), cookies=genereateCookies(), stream=True)

    if resp.status_code == 200:
        doc = pq(resp.text)
        links = []

        for a in doc.find("a").items():
            text = a.text().strip()
            if a.attr("href") and text:
                links.append({
                    "title": text,
                    "href": parse.urljoin(parentUrl, a.attr("href"))
                })

        return links

    else:
        logging.error("failed get url %s status_code=%d " % (url, resp.status_code))

    return []


def export_wiki(wiki_title, wiki_page_url, dir):
    if "STONE" in wiki_page_url:
        return
    if not os.path.exists(dir):
        os.makedirs(dir)

    export_url = "%s/spaces/flyingpdf/pdfpageexport.action?pageId=%s" % parse_host_pageId_fromurl(wiki_page_url)
    if "/" in wiki_title:
        wiki_title = wiki_title.replace("/", "or")
    save_file(export_url, dir + "/" + wiki_title + ".pdf")

    subpages = get_sub_pages_url(wiki_page_url)
    if subpages:
        parentdir = dir + "/" + wiki_title
        for subpage in subpages:
            export_wiki(subpage["title"], subpage["href"], parentdir)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    export_wiki(wiki_title, wiki_page_url, dir)
