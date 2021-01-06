import requests
from bs4 import BeautifulSoup

year = '2020'
mykey = 'Individual Key'

for month in range(1,13):
    # int형으로 받은 숫자 중 10이하 한자리 수면 0을 붙여서 string으로 변환하고,
    # 아니면 그대로 string형으로 변환
    if month < 10:
        month = '0' + str(month)
    else:
        month = str(month)

    url = ' http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo?solYear=%s&solMonth=%s&ServiceKey=%s' % (year, month, mykey)
    get_data = requests.get(url)
    soup = BeautifulSoup(get_data.content, 'html.parser')
    table = soup.find_all('locdate')
    for i in table:
        print(i.text)
