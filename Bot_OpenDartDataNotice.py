from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import sqlite3
import pandas as pd

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

        print('[기업공시알림]\n%s\t%s_%s\n%s\n%s\n' % (company,  date, time, report, link))

if __name__ == '__main__':
    Search()