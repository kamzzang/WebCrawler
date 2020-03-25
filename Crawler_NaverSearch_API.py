import pandas as pd
import numpy as np

import urllib.request

import os
import json


admin_info_file = os.getenv('APPLICATION_ADMIN_INFO') # 환경변수에서 해당 이름의 변수 값(개인정보 json 링크)받아옴
with open(admin_info_file, 'r') as f:
    admin_info = json.load(f)                         # json 파일 로드

client_key = admin_info['naverapi']['id']             # 필요한 정보 저장, 여기서는 naver api의 key
client_secret = admin_info['naverapi']['pw']          # 필요한 정보 저장, 여기서는 naver api의 pw

titles = []
descriptions = []
adress = []
links = []
df = pd.DataFrame()

def search(target, word):
    urls = {'blog': 'https://openapi.naver.com/v1/search/blog.json?query=',
            'kin': 'https://openapi.naver.com/v1/search/kin.json?query=',
            'local': 'https://openapi.naver.com/v1/search/local.json?query='
            }
    # 한글등 non-ASCII text를 URL에 넣을 수 있도록 "%" followed by hexadecimal digits 로 변경
    # URL은 ASCII 인코딩셋만 지원하기 때문임
    encText = urllib.parse.quote_plus(word)
    if target == 'local':
        display = '30'
    else:
        display = '100'

    url = urls[target] + encText + "&display=" + display

    # urllib.request.Request()는 HTTP Header 변경시에 사용함
    # 네이버에서도 다음 HTTP Header 키를 변경해야하기 때문에 사용함
    # HTTP Header 변경이 필요없다면, 바로 urllib.request.urlopen()함수만 사용해도 됩
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_key)
    request.add_header("X-Naver-Client-Secret", client_secret)

    # urllib.request.urlopen 메세드로 크롤링할 웹페이지를 가져옴
    response = urllib.request.urlopen(request)

    # getcode() 메서드로 HTTP 응답 상태 코드를 가져올 수 있음
    rescode = response.getcode()

    # HTTP 요청 응답이 정상적일 경우, 해당 HTML 데이터를 수신되었기 때문에 필요한 데이터 추출이 가능함
    # HTTP 요청에 대한 정상응답일 경우, HTTP 응답 상태 코드 값이 200이 됩니다.
    if (rescode == 200):
        # response.read() 메서드로 수신된 HTML 데이터를 가져올 수 있음
        response_body = response.read()
        # 네이버 Open API를 통해서 수신된 데이터가 JSON 포멧이기 때문에,
        # JSON 포멧 데이터를 파싱해서 사전데이터로 만들어주는 json 라이브러라를 사용
        data = json.loads(response_body)  # .decode('utf-8'))
        # json.loads() 메서드를 사용해서 data 에 수신된 데이터를 사전 데이터로 분석해서 자동으로 만들어줌

        # print (data['items'][0]['title'].replace('<b>','').replace('</b>',''))
        # print (data['items'][0]['description'].replace('<b>','').replace('</b>',''))
        print(data['items'])

        cnt = 0
        while cnt < len(data['items']):
            titles.append(
                data['items'][cnt]['title'].replace('<b>', '').replace('</b>', '').replace('\u263a', '').replace(
                    '\u20a9', '').replace('\u2764', '').replace('\u2013', ''))

            descriptions.append(
                data['items'][cnt]['description'].replace('<b>', '').replace('</b>', '').replace('\u263a', '').replace(
                    '\u20a9', '').replace('\u2764', '').replace('\u2013', ''))

            # adress.append(0)

            links.append(data['items'][cnt]['link'])

            cnt += 1

    else:
        print("Error Code:" + rescode)


def SaveCSV():
    df['TITLE'] = titles
    df['DESC'] = descriptions
    # df['ADRESS'] = adress
    df['LINK'] = links

    # print(df)
    df.to_csv("Result.csv", encoding='cp949')


if __name__ == '__main__':
    word = '경주 맛집'
    target = ['blog', 'kin'] # 블로그 & 지식인 검색 실행
    # target = ['local'] # 네이버 플레이스에서 30깨까지 받는데 실제 5Page 내용까지임, 총 20Page
    for i in target:
        search(i, word)

    SaveCSV()


