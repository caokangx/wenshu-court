"""
新版文书网的demo(2019-09-01后的)
"""
import json
from datetime import datetime
from urllib import parse
import execjs

import requests

from wenshu_utils.cipher import CipherText
from wenshu_utils.des3 import des3decrypt
from wenshu_utils.pageid import PageID
from wenshu_utils.token import RequestVerificationToken

API = "http://120.78.76.198:8000/wenshu"


class NewDemo:
    url: parse.ParseResult = parse.urlparse("http://wenshu.court.gov.cn/website/parse/rest.q4w")

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest"
        })
        self.session.post(self.url.geturl())

    def _request(self, data: dict) -> requests.Response:

        response = self.session.post(self.url.geturl(), data=data)
        print(data)
        if response.status_code != 200:
            raise Exception(response.status_code)

        json_data = response.json()

        if not json_data["success"]:
            print("Request failed. url=%s \n" % (self.url.geturl()))
            return False

        plain_text = des3decrypt(cipher_text=json_data["result"],
                                 key=json_data["secretKey"],
                                 iv=datetime.now().strftime("%Y%m%d"))

        result = json.loads(plain_text)

        return result


def WenShuCrawler():
    demo = NewDemo()

    keywords = open('keywords.txt', 'r')
    f = open('test.txt', 'w')

    for line in keywords.readlines():
        line = line.strip().split(' ')
        length = len(line)
        for i in range(length):
            keyword = line[0] + line[i + 1]
            print(keyword)
            data_page = get_list_page_payload(keyword)

            for i in range(10):
                data_page["pageNum"] = i + 1

                result_page = demo._request(data_page)

                if not result_page:
                    continue

                for docId in result_page["relWenshu"].keys():
                    data_doc = get_detail_page_payload(docId)

                    print("trying to get detail page, docid =%s" % docId)
                    result_doc = demo._request(data_doc)
                    print("get detail page success", result_doc)
                    f.write(str(result_doc) + '\n')

    f.close()


def get_list_page_payload(keyword: str):
    query = {"key": "s21", "value": keyword}

    return {
        "pageId": PageID(),
        "s21": keyword,
        "sortFields": "s50:desc",
        "ciphertext": CipherText(),
        "pageNum": 1,
        "queryCondition": json.dumps([query]),
        "cfg": "com.lawyee.judge.dc.parse.dto.SearchDataDsoDTO@queryDoc",
        "__RequestVerificationToken": RequestVerificationToken(24),
    }


def get_detail_page_payload(docId: str):
    return {
        "docId": docId,
        "ciphertext": CipherText(),
        "cfg": "com.lawyee.judge.dc.parse.dto.SearchDataDsoDTO@docInfoSearch",
        "__RequestVerificationToken": RequestVerificationToken(24),
    }


if __name__ == '__main__':
    demo = NewDemo()
    # demo.list_page()
    # demo.detail_page()
    WenShuCrawler()
