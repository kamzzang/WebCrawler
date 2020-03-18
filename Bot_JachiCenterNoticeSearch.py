import pandas as pd
from pandas import DataFrame

from _datetime import datetime
from bs4 import BeautifulSoup
from urllib.request import urlopen

import pandas.io.sql as pd_sql
import sqlite3

import telepot

import logging

import json
import os

admin_info_file = os.getenv('APPLICATION_ADMIN_INFO') # 환경 변수에 저장한 중요 개인 정보 불러옴
with open(admin_info_file, 'r') as f:
    admin_info = json.load(f)

token = admin_info['telegram']['token'] # "Individual Telegram Token"
Bot_ID = admin_info['telegram']['id']['mc'] # "Receiver's Telegram ID"

Bot = telepot.Bot(token)

dt = datetime.now()

def DatatoSQL(df, dong):
    con = sqlite3.connect("JachiCenterNotice.db")

    df.to_sql(dong, con, if_exists='append')

    # 중복데이터 제거
    sql = "DELETE FROM " + dong + " WHERE rowid NOT IN  (SELECT Max(rowid) FROM " + dong + " GROUP BY TITLE order by TITLE)"
    pd_sql.execute(sql, con)
    con.commit()
    con.close()

    logger.info("%s동 정보 DB 저장 완료" % (dong))

def Holidaycheck():
    today = dt.today()
    month = today.month
    if month < 10:
        month = '0' + str(month)
    else:
        month = str(month)
    day = today.day
    if day < 10:
        day = '0' + str(day)
    else:
        day = str(day)
    today = str(today.year) + month + day

    con = sqlite3.connect("Holiday.db")
    df = pd.read_sql('select * from Holiday ORDER BY Holiday ASC', con=con)
    con.close()

    days = []
    for i in range(0, len(df)):
        days.append(df['Holiday'][i])

    if today in days:
        return False    # 공휴일
    else:
        return True     # 평일

def Check(dong):
    con = sqlite3.connect("JachiCenterNotice.db")
    df = pd.read_sql('select * from ' + dong + ' ORDER BY DATE ASC', con=con)
    con.close()
    
    title = []
    date = []
    for i in range(0,len(df)):
        title.append(df['TITLE'][i])
        date.append(df['DATE'][i])
        
    return title, date

def Search(dong):    
    #print(dong, "주민센터 공지게시판 확인")
    try:
        urls = {'동백' : 'http://jachi.giheunggu.go.kr/_bbsplus/list.asp?code=tbl_community_notice&block=1&page=1&strSearch_text=&strSearch_div=&bd_gubn=8&mnuflag=&bd_gubn_code=all',
                '마북' : 'http://jachi.giheunggu.go.kr/_bbsplus/?mnuflag=&code=tbl_community_notice&bd_gubn=7',
                '보정' : 'http://jachi.giheunggu.go.kr/_bbsplus/?mnuflag=&code=tbl_community_notice&bd_gubn=9',
                '구성' : 'http://jachi.giheunggu.go.kr/_bbsplus/?mnuflag=&code=tbl_community_notice&bd_gubn=4',
                '죽전1' : 'http://jumin.sujigu.go.kr/jj01/sub/sub_04_01_list.asp',
                '죽전2' : 'http://jumin.sujigu.go.kr/jj02/sub/sub_04_01_list.asp'
                }

        url = urls[dong]
        data = urlopen(url).read()
        soup = BeautifulSoup(data, 'html.parser')

        titles = soup.find_all('td')  # , class_ = 'subject')

        data = []
        for i in titles:
            data.append(i.text.replace('\xa0', ''))
        # print(data)
        title_new = []
        date_new = []
        cnt = 0
        while (cnt < len(data)):
            if cnt == 1 or (cnt - 1) % 6 == 0:
                title_new.append(data[cnt])
                date_new.append(data[cnt + 3])
                cnt += 6
            else:
                cnt += 1

        print(dong, '신규 공지 여부 확인')
        title_old, date_old = Check(dong)

        num = 1
        msg = []
        new_msg = False
        for i, j in zip(date_new, title_new):  # zip명령어는 두개의 인덱스가 동시에 반복하도록 하기 위함
            if (i not in date_old) and (j not in title_old):
                new_msg = True
                msg.append(str(num) + '. ' + j + '\n' + i + '\n\n')
            num += 1

        df = DataFrame()
        if new_msg == True:
            print(dong, '신규 공지 확인됨')
            logger.info("%s동 신규 공지 확인됨" % (dong))

            df['TITLE'] = title_new
            df['DATE'] = date_new
            df = df[['DATE', 'TITLE']]
            df = df.set_index('DATE', inplace=False)
            DatatoSQL(df, dong)

            msg_final = "".join(msg)  # 리스트 내부 인자들을 전부 합치기. ""안에 기호를 넣으면 기호 포함되어 합쳐짐
            Bot.sendMessage(Bot_ID, dong + "동 주민센터 공지" + "\n" + msg_final)
            logger.info("텔레그램 메세지 발송")
        else:
            print(dong, '신규 공지 없음')
            logger.info("%s동 신규 공지 없음" % (dong))

    except Exception as e:
        print("Error : ", e)
        logger.debug("%s동 게시판 확인중 에러 : %s" % (dong, e))

if __name__ == '__main__':
    logger = logging.getLogger("주민센터 게시판 정보 크롤러")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s | %(filename)s:%(lineno)s] %(asctime)s >> %(message)s')

    file_handler = logging.FileHandler('JachiCenterBot.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    workday = Holidaycheck()
    if workday == True:
        logger.info("Bot start!!!")
        dong = ['동백', '구성', '마북', '보정', '죽전1', '죽전2']
        for i in dong:
            logger.info("%s동 게시판 확인" % (i))
            Search(i)
    else:
        logger.info("공휴일로 봇 미작동")
    