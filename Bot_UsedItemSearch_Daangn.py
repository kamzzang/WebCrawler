import requests
from urllib import parse

from bs4 import BeautifulSoup

import pandas as pd
import sqlite3
import telepot

# 텔레그램 셋팅 ************************************************************
token = "XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" # 텔레그램 Bot 토근

bot = telepot.Bot(token)
Bot_ID = 'XXXXXXXXX' # 수신자 ID

# 텔레그램 메시지 전송 함수
def Sendmsg(msg):
    bot.sendMessage(Bot_ID, msg)
# ************************************************************************


# 신규 데이터 DB 저장 함수
def DatatoSQL(df):
    con = sqlite3.connect("XXXXX.db") # db 파일명 사용자 임의 선정
    df.to_sql('ITEM', con, if_exists='append', index=False)
    con.close()


# 이전에 저장한 DB와 비교를 위해 불러옴
def Check():
    try:
        con = sqlite3.connect("XXXXX.db") # db 파일명 사용자 임의 선정
        df = pd.read_sql("SELECT * from ITEM ", con=con)
        con.close()

        item_name = df['ID'].tolist() # 동일 매물은 제외시키기 위해서 작성자만 리스트로 받음
        return item_name

    except Exception as e:
        return []


# 입력 매물 검색
def Search(search_word):
    # 크롤링 결과 저장 변수
    data = {'Title': [],
            'Region': [],
            'Price': [],
            'Link': [],
            'ID': []}

    search_word = search_word.split(" ")
    url = 'https://www.daangn.com/search/{}%20{}'.format(search_word[0], search_word[1])

    # 봇으로 접근 시 차단될 수도 있어 유저 정보를 같이 보내기 위함함
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}

    r = requests.get(url, headers=headers)

    soup = BeautifulSoup(r.text, 'html.parser')

    contents = soup.find_all('article', class_ = 'flea-market-article flat-card')

    for i in contents:
        title = i.find('span') # 제목
        region = i.find('p', class_ = 'article-region-name')  # 지역
        price = i.find('p', class_ = 'article-price')         # 가격
        link = 'https://www.daangn.com' + i.find('a')['href'] # 링크

        data['Title'].append(title.text.strip())
        data['Region'].append(region.text.strip())
        data['Price'].append(price.text.strip())
        data['Link'].append(link)
        data['ID'].append(link.split('/')[-1]) # DB의 기존 자료와 비교하기 위한 식별자

    df = pd.DataFrame(data)
    print(df)

    check_list = Check() # 기존 저장된 매물 링크 주소 리스트

    for idx in data['ID']:
        # 크롤링으로 받은 데이터의 링크의 마지막 주소가 기존 리스트에 없으면 메시지 전송/데이터 저장
        if idx not in check_list:
            # 메시지 내용 : 게시글 제목 + 지역 + 가격 + 링크 URL
            pos = data['ID'].index(idx)
            msg = '당근마켓 매물 알림\n{}\n{}\n{}\n{}'.format(data['Title'][pos], data['Region'][pos], data['Price'][pos], data['Link'][pos])
            print(msg)

            Sendmsg(msg) # 메시지 전송
            DatatoSQL(df.loc[df['ID']==idx]) # 데이터 DB 저장


if __name__ == '__main__':
    Search('용인 구글홈')