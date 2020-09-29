import time
from _datetime import datetime

import pandas as pd
from pandas import DataFrame

import pandas.io.sql as pd_sql
import sqlite3

import logging

from bs4 import BeautifulSoup
from urllib.request import urlopen
from selenium import webdriver

import telepot

import json
import os

admin_info_file = os.getenv('APPLICATION_ADMIN_INFO') # 환경 변수에 저장한 중요 개인 정보 불러옴
with open(admin_info_file, 'r') as f:
    admin_info = json.load(f)

token = admin_info['telegram']['token'] # "Individual Telegram Token"
Bot_ID = admin_info['telegram']['id']['mc'] # "Receiver's Telegram ID"

dt = datetime.now()

def DatatoSQL(df, resort):
    con = sqlite3.connect("SkiSeasonBot.db")

    df.to_sql(resort, con, if_exists='append')

    # 중복데이터 제거
    sql = "DELETE FROM " + resort + " WHERE rowid NOT IN  (SELECT Max(rowid) FROM " + resort + " GROUP BY TITLE order by TITLE)"
    pd_sql.execute(sql, con)
    con.commit()
    con.close()

    logger.info("%s 스키장 게시판 정보 DB 저장 완료" % (resort))

def Check(resort):
    try:
        con = sqlite3.connect("SkiSeasonBot.db")
        df = pd.read_sql('select * from ' + resort + ' ORDER BY DATE ASC', con=con)
        con.close()

        title = []
        date = []
        for i in range(0, len(df)):
            title.append(df['TITLE'][i])
            date.append(df['DATE'][i])

        return title, date

    except Exception as e:
        logger.debug("DB 불러오기 에러")


def crawler_jisan(resort):
    try:
        url = 'https://www.jisanresort.co.kr/jisaninfo/news.asp'

        data = urlopen(url).read()
        soup = BeautifulSoup(data, 'html.parser')

        titles = soup.find_all('p', class_='tit')
        dates = soup.find_all('p', class_='date')

        title_new = []
        date_new = []
        for i in titles:
            title_new.append(i.text.replace('\n', ' '))
        # print(title_new)

        for i in dates:
            date_new.append(i.text.replace('\n', ' '))
        # print(date_new)

        return title_new, date_new

    except Exception as e:
        print("Error : ", e)
        logger.debug("%s 리조트 게시판 확인중 에러 : %s" % (resort, e))

def crawler_oak(resort):
    try:
        url = 'http://www.oakvalley.co.kr/oak_new/new_skinotice.asp'

        data = urlopen(url).read()
        soup = BeautifulSoup(data, 'html.parser')

        texts = soup.find_all('td')
        data = []
        for i in texts:
            data.append(i.text)

        title_new = []
        date_new = []
        cnt = 0
        while (cnt < len(data)):
            if cnt == 1 or (cnt - 1) % 4 == 0:
                title_new.append(data[cnt])
                date_new.append(data[cnt + 1])
                cnt += 4
            else:
                cnt += 1

        del (title_new[-1])
        del (date_new[-1])

        return title_new, date_new

    except Exception as e:
        print("Error : ", e)
        logger.debug("%s 리조트 게시판 확인중 에러 : %s" % (resort, e))

def crawler_phoenix(resort):
    try:
        url = 'https://phoenixhnr.co.kr/page/customer/notice?q%5BhmpgDivCd%5D=PP&page=1&size=10'

        web = webdriver.Chrome('chromedriver.exe')
        web.get(url)
        time.sleep(3)
        html_source = web.page_source
        web.close()

        soup = BeautifulSoup(html_source, 'html.parser')

        texts = soup.find_all('td')
        data = []
        for i in texts:
            data.append(i.text.replace('\n','').replace('\t',''))

        title_new = []
        date_new = []
        cnt = 0
        while(cnt < len(data)):
            if cnt  == 2 or (cnt + 2) % 4 == 0:
                title_new.append(data[cnt])
                date_new.append(data[cnt+1])
                cnt += 4
            else:
                cnt+=1

        # print(title_new)
        # print(date_new)

        return title_new, date_new

    except Exception as e:
        print("Error : ", e)
        logger.debug("%s 리조트 게시판 확인중 에러 : %s" % (resort, e))

def crawler_welli(resort):
    try:
        url = 'https://www.wellihillipark.com/sub3/mysungwoo/news/list.asp'

        web = webdriver.Chrome('chromedriver.exe')
        web.get(url)
        time.sleep(3)
        html_source = web.page_source
        web.close()

        soup = BeautifulSoup(html_source, 'html.parser')

        texts = soup.find_all('td')#, class_ = 'al')
        data = []
        for i in texts:
            data.append(i.text.replace('\n','').replace('\t','').replace('\xa0\t\t','').replace('\xa0','').replace(' ',''))

        title_new = []
        date_new = []
        cnt = 0
        while (cnt < len(data)):
            if cnt == 1 or (cnt - 1) % 4 == 0:
                title_new.append(data[cnt])
                date_new.append(data[cnt + 1])
                cnt += 4
            else:
                cnt += 1

        del (title_new[-1])
        del (date_new[-1])

        return title_new, date_new

    except Exception as e:
        print("Error : ", e)
        logger.debug("%s 리조트 게시판 확인중 에러 : %s" % (resort, e))

def crawler_high1(resort):
    try:
        url = 'https://www.high1.com/ski/selectBbsNttList.do?key=756&bbsNo=85&nttNo=131137&searchCtgry=%EC%8A%A4%ED%82%A4&searchCnd=all&searchKrwd=&integrDeptCode=&pageIndex=1'

        data = urlopen(url).read()
        soup = BeautifulSoup(data, 'html.parser')

        texts = soup.find_all('td')#, class_ = 'left')
        data = []
        for i in texts:
            data.append(i.text.replace('\n','').replace('\t','').replace('\r',''))
        # print(data) #데이터 내용 확인 : 제목 인덱스 - 2, 7, 12 / 날짜 인덱스 - 3, 8, 13

        title_new = []
        date_new = []
        cnt = 0
        cnt_data = []
        while (cnt < len(data)):
            if cnt == 2 or (cnt + 3) % 5 == 0: # 제목 첫 인덱스인 '2', 연속하는 조건들의 동일 조건 확인 7, 12는 3을 더하면 5의 배수가 되므로 3을 더해서 5를 나눈 값이 0
                title_new.append(data[cnt])
                date_new.append(data[cnt + 1])
                cnt_data.append(cnt)
                cnt += 3 # 첫 조건에 만족해서 저장하고 나면 바로 다음 인덱스 조건에 만족할 수 있게 카운트를 더해버립
            else:
                cnt += 1


        return title_new, date_new

    except Exception as e:
        # print("Error : ", e)
        logger.debug("%s 리조트 게시판 확인중 에러 : %s" % (resort, e))

def Search(resort):
    print(resort, "스키장 리조트 공지게시판 확인")
    try:
        if resort == '지산':
            title_new, date_new = crawler_jisan(resort)
        elif resort == '오크밸리':
            title_new, date_new = crawler_oak(resort)
        elif resort == '휘닉스파크':
            title_new, date_new = crawler_phoenix(resort)
        elif resort == '웰리힐리':
            title_new, date_new = crawler_welli(resort)

        title_old, date_old = Check(resort)

        num = 1
        msg = []
        new_msg = False
        for i, j in zip(date_new, title_new):  # zip명령어는 두개의 인덱스가 동시에 반복하도록 하기 위함
            if (i not in date_old) and (j not in title_old):
                new_msg = True
                msg.append(str(num) + '. ' + i + '\n' + j + '\n\n')
            num += 1
        # print(new_msg)
        # print(msg)
        df = DataFrame()
        if new_msg == True:
            print(resort, '신규 공지 확인됨')
            logger.info("%s 리조트 신규 공지 확인됨" % (resort))

            df['TITLE'] = title_new
            df['DATE'] = date_new
            df = df[['DATE', 'TITLE']]
            df = df.set_index('DATE', inplace=False)

            DatatoSQL(df, resort)

            msg_final = "".join(msg)  # 리스트 내부 인자들을 전부 합치기. ""안에 기호를 넣으면 기호 포함되어 합쳐짐

            # 결과 텔레그램 전송
            bot = telepot.Bot(token)
            bot.sendMessage(Bot_ID, resort + " 리조트 공지" + "\n" + msg_final)
            logger.info("텔레그램 메세지 발송")
        else:
            print(resort, '신규 공지 없음')
            logger.info("%s 리조트 신규 공지 없음" % (resort))

    except Exception as e:
        print("Error : ", e)
        logger.debug("%s 리조트 게시판 확인중 에러 : %s" % (resort, e))


if __name__ == '__main__':
    logger = logging.getLogger("스키장 공지 게시판 정보 크롤러")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s | %(filename)s:%(lineno)s] %(asctime)s >> %(message)s')

    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)

    file_handler = logging.FileHandler('SkiSeasonBot.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info("Bot start!!!")
    resort = ['지산', '웰리힐리', '휘닉스파크', '오크밸리']

    for i in resort:
        logger.info("%s 리조트 게시판 확인" % (i))
        Search(i)
    logger.info("Bot end!!!")