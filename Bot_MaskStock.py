import requests
import pandas as pd
import telepot
import json
import os
import folium

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
  "도로명주소": [],
  "생성일": [],
  "상호명": [],
  "유형": [],
  "재고상태": [],
    "위도": [],
    "경도":[]
}
# 추가 데이터 : lat(위도), lng(경도), stock_at(입고시간)
for store in stores:
    data['도로명주소'].append(store['addr'])              # 판매처 주소
    data['생성일'].append(store['created_at'])  # 데이터 생성일자
    data['상호명'].append(store['name'])              # 이름
    data['유형'].append(store['type'])              # 판매처 유형
    data['재고상태'].append(store.get('remain_stat', '')) # 재고 상태
    data['위도'].append(store['lat'])
    data['경도'].append(store['lng'])

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

df['상태'] = df['재고상태'].apply(status)

# 재고 상태 항목 설명으로 변경
df['재고상태'] = df['재고상태'].replace('plenty','100개이상').\
    replace('some','30~99개').replace('few','2~29개').\
    replace('break','판매중지').replace('empty','0~1개')

# 집 주변 약국 리스트(이 약국 이외에는 정보 받지 않음)
name_list = ['행복한약국','서울팜약국','동백바른약국','동백사랑약국','메디필약국','정다운약국','건강소망약국']
df_final = df[df['상호명'].isin(name_list)] # 약국 리스트에 포함된 약국 데이터만 다시 저장

df_final = df_final.sort_values(by='상태').reset_index(drop=True) # 재고 상태에 따라 정렬(많을 수록 먼저 나옴)

# 텔레그램 메세지를 만들기 위해 약국 이름과 재고 상태를 리스트로 저장
name = list(df_final['상호명'])
status = list(df_final['재고상태'])

# for문을 돌면서 메세지 만듬
msg = '<공정 마스크 현황 알림>\nUpdated : %s\n' % (df_final['생성일'][0])
for i in range(len(name)):
    msg = msg + str(i+1) + '.' + name[i] + " : " + status[i] + "\n"

# 결과 텔레그램 전송
bot = telepot.Bot(token)
bot.sendMessage(Bot_ID, msg)

# 텔레그램 메세지
# <공적 마스크 현황 알림>
# Updated : 2020/04/08 22:10:00
# 1.건강소망약국 : 100개이상
# 2.정다운약국 : 100개이상
# 3.메디필약국 : 0~1개
# 4.동백사랑약국 : 0~1개
# 5.행복한약국 : 0~1개
# 6.서울팜약국 : 판매중지
# 7.동백바른약국 : 판매중지

def show_marker_map(df):
    map = folium.Map(location=[df['위도'].mean(), df['경도'].mean()], zoom_start=16) # 전체 위도와 경도의 중심부로 지도 위치를 설정
    for n in df.index:
        shop_name = df.loc[n, '상호명']
        # 재고 상태에 따라 색상을 변경하기 위한 조건문
        if df['재고상태'][n] == '100개이상':
            icon_color = 'blue'
        elif df['재고상태'][n] == '30~99개':
            icon_color = 'yellow'
        elif df['재고상태'][n] == '2~29개':
            icon_color = 'red'
        elif df['재고상태'][n] == '판매중지' or df['재고상태'][n] == '0~1개':
            icon_color = 'gray'

        folium.Marker([df.loc[n, '위도'], df.loc[n, '경도']],
                      popup=shop_name,
                      icon=folium.Icon(color=icon_color)).add_to(map)

    return map

show_marker_map(df_final)