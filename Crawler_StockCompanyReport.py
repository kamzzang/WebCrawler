# -*- coding: utf-8 -*-
import os, glob, sys, getopt
from pytz import timezone, utc

import re
import calendar

import datetime, time
from datetime import timedelta
import urllib.request
import requests, json
from http.cookiejar import CookieJar
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from pandas import DataFrame
import pandas.io.sql as pdsql
from matplotlib import dates

import mysql.connector

import logging
import logging.handlers


MySQL_POOL_SIZE = 2

데이타베이스_설정값 = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'XXXXXXXXXX',
    'database': 'XXXXXXXXXX',
    'raise_on_warnings': True,
}

class NumpyMySQLConverter(mysql.connector.conversion.MySQLConverter):
    """ A mysql.connector Converter that handles Numpy types """

    def _float32_to_mysql(self, value):
        return float(value)

    def _float64_to_mysql(self, value):
        return float(value)

    def _int32_to_mysql(self, value):
        return int(value)

    def _int64_to_mysql(self, value):
        return int(value)

    def _timestamp_to_mysql(self, value):
        # print(type(value))
        # return value.strftime("%Y-%m-%d %H:%M:%S")
        # print(value.to_pydatetime())
        return value.to_datetime()

def mysqlconn():
    conn = mysql.connector.connect(pool_name="stockpool", pool_size=MySQL_POOL_SIZE, **데이타베이스_설정값)
    conn.set_converter_class(NumpyMySQLConverter)
    return conn

def get_webpage(url, encoding=""):
    cj = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95  Safari/537.36')]

    respstr = ""
    try:
        op = opener.open(url)
        sourcecode = op.read()
    except Exception as e:
        time.sleep(1)
        op = opener.open(url)
        sourcecode = op.read()

    encodingmethod = op.info().get_param('charset')
    if encodingmethod == None:
        if encoding != "":
            encodingmethod = encoding

    if encoding != "":
        encodingmethod = encoding

    try:
        respstr = sourcecode.decode(encoding=encodingmethod, errors='ignore')
    except Exception as e:
        respstr = sourcecode.decode(encoding="cp949", errors='ignore')

    opener.close()

    return respstr

def get_company_report_fnguide(시작일='20150101', 종료일='20150101'):
    url = "http://comp.fnguide.com/SVO2/asp/SVD_Report_Summary_Data.asp?fr_dt=%s&to_dt=%s&stext=&check=all&sortOrd=5&sortAD=A&_=2" % (시작일, 종료일)
    respstr = get_webpage(url, encoding="utf8")

    # soup = BeautifulSoup(respstr)
    soup = BeautifulSoup(respstr, "lxml")

    result = []
    for i in soup.find_all('tr'):
        arry = i.find_all("td")
        날짜 = arry[0].text.strip().replace('/','-')

        line1 = arry[1].text.strip().replace('\n', ' ')
        종목명 = line1.split(' ')[0]
        코드 = line1.split(' ')[1].replace('A','')
        if len(코드) < 6:
            종목명 = '%s %s' % (종목명, 코드)
            코드 = line1.split(' ')[2].replace('A','')
        if len(코드) < 6:
            종목명 = '%s %s' % (종목명, 코드)
            코드 = line1.split(' ')[3].replace('A','')

        line131 = line1.split(' ')[2:]
        추천사유 = (' '.join(line131)).strip()
        의견 = arry[2].text.strip()
        try:
            목표가 = int(arry[3].text.strip().replace(',',''))
        except Exception as e:
            목표가 = 0
        try:
            추천일가격 = arry[4].text.strip().replace(',','')
        except Exception as e:
            추천일가격 = 0

        line51 = arry[5].text.strip()[:-3]
        line52 = arry[5].text.strip()[-3:]
        추천증권사 = "%s %s" % (line51, line52)

        result.append([날짜, 코드, 종목명, 의견, 목표가, 추천일가격, 추천증권사, 추천사유])

    df = DataFrame(data=result, columns=['날짜', '코드', '종목명', '의견', '목표가', '추천일가격', '추천증권사', '추천사유'])
    df.set_index('날짜', inplace=True)

    return df

def build_broker_report(시작일='20150101', 종료일='20150101'):
    df = get_company_report_fnguide(시작일=시작일, 종료일=종료일)
    df.reset_index(inplace=True)
    # print(df)
    values = df.values
    # print(values)

    conn = mysqlconn()

    cursor = conn.cursor()
    cursor.executemany("replace into 증권사추천주(일자,종목코드,종목명,의견,목표가,추천일가격,추천증권사,추천사유) values(%s, %s, %s, %s, %s, %s, %s, %s)", df.values.tolist())
    conn.commit()
    conn.close()

def time_print(start, middle, end):
    print("[{}] 걸린시간 : {} 전체걸린시간 : {}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), end - middle,
                                              end - start))

if __name__ == '__main__':

    start = time.time()
    middle = time.time()

    if len(sys.argv) == 1:
        시작일 = "{:%Y%m}01".format(datetime.datetime.now())
        종료일 = "{:%Y%m%d}".format(datetime.datetime.now())
    if len(sys.argv) == 2:
        시작일 = sys.argv[1]
        종료일 = "{:%Y%m%d}".format(datetime.datetime.now())
    if len(sys.argv) == 3:
        시작일 = sys.argv[1]
        종료일 = sys.argv[2]

    build_broker_report(시작일=시작일, 종료일=종료일)

    # ---------------------------------------------------
    #
    # year = ['2013', '2014', '2015']
    # month = ['{:02d}'.format(x) for x in range(1,13)]
    # for y in year:
    #     for m in month:
    #         print('%s년 %s월' %(y, m))
    #         build_broker_report(시작일=y+m+'01', 종료일=y+m+'31')
    #
    # print("완료")


    # ---------------------------------------------------
    #
    # build_broker_report(시작일='20151201', 종료일='20151212')

    end = time.time()
    time_print(start, middle, end)