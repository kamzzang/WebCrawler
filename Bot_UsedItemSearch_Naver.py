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

# 크롤링 결과 저장 변수
# 전역 변수로 사용할 수도 있어 여기에 선언
# 작성자(닉네임), 제목, 링크 URL 저장함
data = {'Name':[],
        'Title':[],
        'URL':[]}

# 신규 데이터 DB 저장 함수
def DatatoSQL(df):
    con = sqlite3.connect("XXXXXX.db") # db 파일명 사용자 임의 선정
    df.to_sql('ITEM', con, if_exists='append', index=False)
    con.close()

# 이전에 저장한 DB와 비교를 위해 불러옴
def Check():
    try:
        con = sqlite3.connect("XXXXXX.db") # db 파일명 사용자 임의 선정
        df = pd.read_sql("SELECT * from ITEM ", con=con)
        con.close()

        item_name = df['Name'].tolist() # 동일 매물은 제외시키기 위해서 작성자만 리스트로 받음
        return item_name

    except Exception as e:
        return []

# 입력 매물 검색
def Search(search_word):
    # 모바일 URL로 접근(별도로 검색어 입력을 위한 selenium 필요없음)
    url = 'https://m.cafe.naver.com/ArticleSearchList.nhn?search.query=%s&search.menuid=0&search.searchBy=0&search.sortBy=date&search.clubid=10050146&search.option=0&search.defaultValue=1'%(parse.quote(search_word))

    # 봇으로 접근 시 차단될 수도 있어 유저 정보를 같이 보내기 위함함
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}

    r = requests.get(url, headers=headers)

    soup = BeautifulSoup(r.text, 'html.parser')

    table = soup.find_all('li')

    for i in table[-20:]:
        # 링크 주소는 모바일로 만들어서 메시지 발송
        link = 'https://m.cafe.naver.com' + i.find('a')['href'] # a 태그의 href

        title = i.find('h3') # h3 태그

        name = i.find('span', class_='name') # span 태그의 name 클래스

        data['Name'].append(name.text.strip())
        data['Title'].append(title.text.strip())
        data['URL'].append(link)

    df = pd.DataFrame(data)
    print(df)

    check_list = Check() # 기존 저장된 매물 등록자 리스트

    for name in data['Name']:
        # 크롤링으로 받은 데이터의 작성자가 기존 리스트에 없으면 메시지 전송/데이터 저장
        if name not in check_list:
            # 메시지 내용 : 게시글 제목 + URL
            msg = '중고나라 매물 알림\n{}\n{}'.format(data['Title'][data['Name'].index(name)], data['URL'][data['Name'].index(name)])

            print(msg)
            Sendmsg(msg) # 메시지 전송
            DatatoSQL(df.loc[df['Name']==name]) # 데이터 DB 저장

if __name__ == '__main__':
    Search('브롬톤')