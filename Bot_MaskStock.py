import requests
import pandas as pd
import telepot
import json
import os

admin_info_file = os.getenv('APPLICATION_ADMIN_INFO') # 환경 변수에 저장한 중요 개인 정보 불러옴
with open(admin_info_file, 'r') as f:
    admin_info = json.load(f)

token = admin_info['telegram']['token'] # "Individual Telegram Token"
Bot_ID = admin_info['telegram']['id']['mc'] # "Receiver's Telegram ID"

address = '경기도 용인시 기흥구 중동' # 마스크 알림 확인 주소
url = 'https://8oi9s0nnth.apigw.ntruss.com/corona19-masks/v1/storesByAddr/json?address=%s'%(address) # API URL

respond = requests.get(url)
json = respond.json()

stores = json['stores']
count = json['count']

data = {
  "addr": [],
  "created_at": [],
  "name": [],
  "type": [],
  "remain_stat": [],
}
# 추가 데이터 : lat(위도), lng(경도), stock_at(입고시간)
for store in stores:
    data['addr'].append(store['addr'])              # 판매처 주소
    data['created_at'].append(store['created_at'])  # 데이터 생성일자
    data['name'].append(store['name'])              # 이름
    data['type'].append(store['type'])              # 판매처 유형
    data['remain_stat'].append(store.get('remain_stat', '')) # 재고 상태

df = pd.DataFrame(data)

def status(data): # 재고 상태에 따른 상태 순위 지정 함수
    if 'plenty' == data:
        return 0
    elif 'some' == data:
        return 1
    elif 'few' == data:
        return 2
    elif 'empty' == data:
        return 3
    elif 'break' == data:
        return 4

df['status'] = df['remain_stat'].apply(status)

# 재고 상태 항목 설명으로 변경
df['remain_stat'] = df['remain_stat'].replace('plenty','100개이상').\
    replace('some','30~99개').replace('few','2~29개').\
    replace('break','판매중지').replace('empty','0~1개')

# 집 주변 약국 리스트(이 약국 이외에는 정보 받지 않음)
name_list = ['행복한약국','서울팜약국','동백바른약국','동백사랑약국','메디필약국','정다운약국','건강소망약국']
df = df[df['name'].isin(name_list)] # 약국 리스트에 포함된 약국 데이터만 다시 저장

df = df.sort_values(by='status').reset_index(drop=True) # 재고 상태에 따라 정렬(많을 수록 먼저 나옴)

# 텔레그램 메세지를 만들기 위해 약국 이름과 재고 상태를 리스트로 저장
name = list(df['name'])
status = list(df['remain_stat'])

# for문을 돌면서 메세지 만듬
msg = '<공정 마스크 현황 알림>\nUpdated : %s\n' % (df['created_at'][0])
for i in range(len(name)):
    msg = msg + str(i+1) + '.' + name[i] + " : " + status[i] + "\n"

# 결과 텔레그램 전송
bot = telepot.Bot(token)
bot.sendMessage(Bot_ID, msg)

# 텔레그램 메세지
# <공정 마스크 현황 알림>
# Updated : 2020/04/08 22:10:00
# 1.건강소망약국 : 100개이상
# 2.정다운약국 : 100개이상
# 3.메디필약국 : 0~1개
# 4.동백사랑약국 : 0~1개
# 5.행복한약국 : 0~1개
# 6.서울팜약국 : 판매중지
# 7.동백바른약국 : 판매중지