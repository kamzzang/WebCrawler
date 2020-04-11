import pandas as pd
import urllib.request
import json

client_key = '네이버 클라우드 플랫폼에 등록한 Application의 Client ID'
client_secret = "네이버 클라우드 플랫폼에 등록한 Application의 Client Secret"

address = '경기도 성남시 분당구 불정로 6 그린팩토리'
# 한글등 non-ASCII text를 URL에 넣을 수 있도록 "%" followed by hexadecimal digits 로 변경
# URL은 ASCII 인코딩셋만 지원하기 때문임
encAdd = urllib.parse.quote_plus(address)

url = 'https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query=%s'%(encAdd)

request = urllib.request.Request(url)
request.add_header("X-NCP-APIGW-API-KEY-ID", client_key)
request.add_header("X-NCP-APIGW-API-KEY", client_secret)

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
    data = json.loads(response_body)
    print(data)
    print(data['addresses'][0]['x'], data['addresses'][0]['y']) # 경도와 위도에 해당하는 x, y값을 출력