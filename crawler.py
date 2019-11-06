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
        })
        # self.session.proxies = # TODO 配置你的代理

    def _request(self, data: dict) -> requests.Response:
        # response = requests.post(API, json={"path": self.url.path, "request_args": data})
        # if response.status_code != 200:
        #     raise Exception(response.text)
        # 
        # kwargs = response.json()

        response = self.session.post(self.url.geturl(), data=data, cookies="")
        print(data)
        if response.status_code != 200:
            raise Exception(response.status_code)

        json_data = response.json()

        plain_text = des3decrypt(cipher_text=json_data["result"],
                                 key=json_data["secretKey"],
                                 iv=datetime.now().strftime("%Y%m%d"))

        result = json.loads(plain_text)

        return result

    def list_page(self):
        """文书列表页"""
        data = {
            "pageId": '69fe95623bbeef68cbab43867cf0ad28',
            # "pageId": PageID()
            "s21": "充电宝",
            "sortFields": "s50:desc",
            "ciphertext": CipherText(),
            "pageNum": 1,
            "pageSize": 15,
            "queryCondition": [{"key": "s21", "value": "充电宝"}],  # 查询条件: s8=案件类型, 03=民事案件
            "cfg": "com.lawyee.judge.dc.parse.dto.SearchDataDsoDTO@queryDoc",
            "__RequestVerificationToken": RequestVerificationToken(24),
        }

        result = self._request(data)
        print(result)

    def detail_page(self):
        """文书详情页"""
        data = {
            "docId": "755d49bd07624acbb66baaf00113517e",  # "4e00b8ae589b4288a725aabe00c0e683",
            "ciphertext": CipherText(),
            "cfg": "com.lawyee.judge.dc.parse.dto.SearchDataDsoDTO@docInfoSearch",
            "__RequestVerificationToken": RequestVerificationToken(24),
        }

        result = self._request(data)
        print(result)


def WenShuCrawler():
    demo = NewDemo()
    data_page = {
        "pageId": PageID(),
        "s21": "充电宝",
        "sortFields": "s50:desc",
        "ciphertext": CipherText(),
        "pageNum": 1,
        "queryCondition": json.dumps([{"key": "s21", "value": "充电宝"}]),  # 查询条件: s8=案件类型, 03=民事案件
        "cfg": "com.lawyee.judge.dc.parse.dto.SearchDataDsoDTO@queryDoc",
        "__RequestVerificationToken": RequestVerificationToken(24),
    }
    data_doc = {
        "docId": "4e00b8ae589b4288a725aabe00c0e683",
        "ciphertext": CipherText(),
        "cfg": "com.lawyee.judge.dc.parse.dto.SearchDataDsoDTO@docInfoSearch",
        "__RequestVerificationToken": RequestVerificationToken(24),
    }
    keywords = open('keywords.txt', 'r')
    f = open('test.txt', 'w')

    query = {
        "key": "s21",
        "value": "充电宝"
    }
    for line in keywords.readlines():
        line = line.strip().split(' ')
        length = len(line)
        for i in range(length):
            keyword = line[0] + line[i + 1]
            print(keyword)
            query["value"] = keyword
            data_page["queryCondition"] = json.dumps(query)
            data_page["s21"] = keyword

            for i in range(10):
                data_page["pageNum"] = i + 1

                result_page = demo._request(data_page)
                # print(result['relWenshu'].keys())
                # if i % 5 == 0:
                #    time.sleep(60)
                for docId in result_page["relWenshu"].keys():
                    data_doc["docId"] = docId
                    print(docId)
                    result_doc = demo._request(data_doc)
                    print(result_doc)
                    f.write(str(result_doc) + '\n')

    f.close()


if __name__ == '__main__':
    demo = NewDemo()
    # demo.list_page()
    demo.detail_page()
    WenShuCrawler()
