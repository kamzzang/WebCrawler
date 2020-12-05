from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import sqlite3
import pandas as pd
import json
import telepot
import os

admin_info_file = os.getenv('APPLICATION_ADMIN_INFO') # 환경 변수에 저장한 중요 개인 정보 불러옴
with open(admin_info_file, 'r') as f:
    admin_info = json.load(f)

token = admin_info['telegram']['token'] # "Individual Telegram Token"
Bot_ID = admin_info['telegram']['id']['mc'] # "Receiver's Telegram ID"
# 결과 텔레그램 전송
bot = telepot.Bot(token)


def Search():
    url = "http://dart.fss.or.kr/dsac001/mainAll.do"
    html = urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')

    trs = soup.findAll('tr')[1:]
    for tr in trs:
        td = tr.findAll('td')

        date = re.sub(r'[\t\n\r ]', '', tr.findAll('td', class_='cen_txt')[1].text)  # 공시날짜
        time = re.sub(r'[\t\n\r ]', '', tr.findAll('td', class_='cen_txt')[0].text)  # 공시시간
        company =re.sub(r'[\t\n\r ]', '', td[1].find('a').text) # 회사명
        report = re.sub(r'[\t\n\r ]', '', tr.findAll('td')[2].find('a').text)  # 보고서명
        link = 'dart.fss.or.kr' + tr.findAll('td')[2].find('a').attrs['href']  # url

        msg = '[기업공시알림]\n%s\t%s_%s\n%s\n%s\n' % (company,  date, time, report, link)
        print(msg)
        bot.sendMessage(Bot_ID, msg)

if __name__ == '__main__':
    Search()