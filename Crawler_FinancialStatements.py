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
import pandas.io.sql as pdsql
import mysql.connector

MySQL_POOL_SIZE = 2

데이타베이스_설정값 = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'password',
    'database': 'database name',
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

def get_company_fundamental_fnguide(code):

    def g(x):
        if type(x) == str:
            return datetime.datetime.strptime(x, '%Y-%m-%d')
        else:
            return x

    url = "http://asp01.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A%s&NewMenuID=11&cID=50&MenuYn=N" % (code)
    respstr = get_webpage(url, encoding="utf8")
    soup = BeautifulSoup(respstr, "lxml")

    # <!--IFRS 별도/연간 -->
    target_table = soup.find("div", class_="um_table", id="highlight_B_Y")
    # print(target_table)
    result = []

    try:
        target_table.find_all('tr')
    except Exception as e:
        print('%s 연간데이터 수집 에러'%(code))
        return (pd.DataFrame(), pd.DataFrame())

    for tr in target_table.find_all('tr'):
        for th in tr.find_all('th'):
            value = "%s" % th.text.replace('(P) : Provisional','').replace('(E) : Estimate','').replace('잠정실적','').replace('컨센서스, 추정치','').replace('(E)','').replace('(P)','').replace('/','-').strip()
            if ('-02' in value):
                value = value + '-28'
            elif ('-04' in value) or ('-06' in value) or ('-09' in value) or ('-11' in value):
                value = value + '-30'
            elif ('-01' in value) or ('-03' in value) or ('-05' in value) or ('-07' in value) or ('-08' in value) or ('-10' in value) or ('-12' in value):
                value = value + '-31'
            result.append(value)

        for td in tr.find_all('td'):
            value = td.text.strip().replace(',','')
            try:
                value = float(value)
            except Exception as e:
                value = 0
            result.append(value)

    result = result[1:]
    dfdata = []
    for x in range(0, len(result), 9):
        if result[x] != '영업이익(발표기준)':
            dfdata.append(result[x:x+9])


    df = pd.DataFrame(data=dfdata, columns = [str(x) for x in range(1,10)]).T
    df.columns = ['날짜', '매출액', '영업이익', '당기순이익', '자산총계', '부채총계', '자본총계', '자본금', '부채비율', '유보율', '영업이익률', '순이익률', 'ROA', 'ROE', 'EPS', 'BPS', 'DPS', 'PER', 'PBR', '발행주식수', '배당수익률']
    df.drop(df.index[[0]], inplace=True)
    df = df.convert_objects(convert_numeric=True)


    # 네이버 증권 영업활동현금흐름 파싱*****************************************************************
    url2 = "http://companyinfo.stock.naver.com/v1/company/cF1001.aspx?cmp_cd=%s&fin_typ=0&freq_typ=Y" % (code)
    get_data = requests.get(url2)
    soup2 = BeautifulSoup(get_data.content, 'html.parser')
    table = soup2.select('th')
    date = []
    idx = []
    cnt = 1

    for i in table:
        if cnt > 3 and cnt <= 7:
            value = i.text.replace('/', '-').replace('(E)', '').replace('\t', '').replace('\n', '').replace('\r','').replace('(IFRS연결)', '').replace('\xa0', '').replace('(IFRS별도)','').replace('(GAAP개별)','')
            if ('-02' in value):
                value = value + '-28'
            elif ('-04' in value) or ('-06' in value) or ('-09' in value) or ('-11' in value):
                value = value + '-30'
            elif ('-01' in value) or ('-03' in value) or ('-05' in value) or ('-07' in value) or ('-08' in value) or (
                '-10' in value) or ('-12' in value):
                value = value + '-31'
            date.append(value)

        if cnt >23:
            idx.append(i.text)

        cnt += 1

    data_list = soup2.select('td')
    data = []
    for i in data_list:
        if i.text == '':
            data.append('0')
        else:
            data.append(i.text)

    temp_list = []
    data_len = 8
    idx_pos = idx.index('영업활동현금흐름')
    for i in range(idx_pos * data_len, idx_pos * data_len + 4):
        temp_list.append(float(data[i].replace(',','')))

    df_temp = pd.DataFrame(data=temp_list, index=date, columns=['영업활동현금흐름'])
    df_temp = df_temp.reset_index()
    df_temp.columns = ['날짜', '영업활동현금흐름']

    if date[0] =='':
        df['영업활동현금흐름'] = temp_list
    else:
        df_year = pd.merge(df, df_temp, left_on='날짜', right_on='날짜', how='outer')
        df_year = df_year.fillna(0)



    #*****************************************************************************************
    # <!--IFRS 별도/분기 -->
    target_table = soup.find("div", class_="um_table", id="highlight_B_Q")

    result = []
    for tr in target_table.find_all('tr'):
        for th in tr.find_all('th'):
            value = "%s" % th.text.replace('(P) : Provisional','').replace('(E) : Estimate','').replace('잠정실적','').replace('컨센서스, 추정치','').replace('(E)','').replace('(P)','').replace('/','-').strip()
            if ('-02' in value):
                value = value + '-28'
            elif ('-04' in value) or ('-06' in value) or ('-09' in value) or ('-11' in value):
                value = value + '-30'
            elif ('-01' in value) or ('-03' in value) or ('-05' in value) or ('-07' in value) or ('-08' in value) or ('-10' in value) or ('-12' in value):
                value = value + '-31'
            result.append(value)

        for td in tr.find_all('td'):
            value = td.text.strip().replace(',','')
            try:
                value = float(value)
            except Exception as e:
                value = 0
            result.append(value)

    result = result[1:]
    dfdata = []
    for x in range(0, len(result), 9):
        if result[x] != '영업이익(발표기준)':
            dfdata.append(result[x:x+9])
    df = pd.DataFrame(data=dfdata, columns = [str(x) for x in range(1,10)]).T
    df.columns = ['날짜', '매출액', '영업이익', '당기순이익', '자산총계', '부채총계', '자본총계', '자본금', '부채비율', '유보율', '영업이익률',
                  '순이익률', 'ROA', 'ROE', 'EPS', 'BPS', 'DPS', 'PER', 'PBR', '발행주식수', '배당수익률']
    df.drop(df.index[[0]], inplace=True)
    df = df.convert_objects(convert_numeric=True)

    # 네이버 증권 분기 영업활동현금흐름 파싱*********************************************************
    date = []
    cnt = 1
    for i in table:
        if cnt > 7 and cnt <= 11:
            value = i.text.replace('/', '-').replace('(E)', '').replace('\t', '').replace('\n', '').replace('\r','').replace('(IFRS연결)', '').replace('\xa0', '').replace('(IFRS별도)', '')
            if ('-02' in value):
                value = value + '-28'
            elif ('-04' in value) or ('-06' in value) or ('-09' in value) or ('-11' in value):
                value = value + '-30'
            elif ('-01' in value) or ('-03' in value) or ('-05' in value) or ('-07' in value) or ('-08' in value) or (
                    '-10' in value) or ('-12' in value):
                value = value + '-31'
            date.append(value)
        cnt += 1

    temp_list = []
    for i in range(idx_pos * data_len + 4, idx_pos * data_len + 8):
        temp_list.append(float(data[i].replace(',', '')))

    df_temp = pd.DataFrame(data=temp_list, index=date, columns=['영업활동현금흐름'])
    df_temp = df_temp.reset_index()
    df_temp.columns = ['날짜', '영업활동현금흐름']

    if date[0] == '':
        df['영업활동현금흐름'] = temp_list
    else:
        df_qtr = pd.merge(df, df_temp, left_on='날짜', right_on='날짜', how='outer')
        df_qtr = df_qtr.fillna(0)


    return (df_year, df_qtr)

def build_fundamental_data():
    conn = mysqlconn()
    cursor = conn.cursor()
    replace_mysql = (
        "replace into 재무정보( 날짜,종목코드,기간구분,매출액,영업이익,당기순이익,자산총계,부채총계,자본총계,자본금,부채비율,유보율,영업이익률,순이익률,ROA,ROE,EPS,BPS,DPS,PER,PBR,발행주식수,배당수익률,영업활동현금흐름) "
        "values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s ) "
    )

    df = pdsql.read_sql_query('select 시장구분, 종목코드, 종목명 from 종목코드 ', con=conn)
    df = df[(df['시장구분'] != 'ETF')]
    del df['시장구분']

    cnt=1
    CODES = list(df.values)
    for code, name in CODES:
        if code[-1] != '0':
            cnt += 1
            continue
        print('FnGuide - %s %s : %s/%s' % (code, name, cnt, len(CODES)))

        try:
            (df_year, df_qtr) = get_company_fundamental_fnguide(code)
        except Exception as e:
            cnt += 1
            print('%s, %s Error : %s' % (code, name, e))
            continue

        try:
            if len(df_year.index) > 0 or len(df_qtr.index) > 0:
                if len(df_year.index) > 0:
                    기간구분 = '년간'
                    for idx, row in df_year.iterrows():
                        날짜, 매출액, 영업이익, 당기순이익, 자산총계, 부채총계, 자본총계, 자본금, 부채비율, 유보율, 영업이익률, 순이익률, ROA, ROE, EPS, BPS, DPS, PER, PBR, 발행주식수, 배당수익률,영업활동현금흐름 = row
                        종목코드 = code
                        d = (날짜,종목코드,기간구분,매출액,영업이익,당기순이익,자산총계,부채총계,자본총계,자본금,부채비율,유보율,영업이익률,순이익률,ROA,ROE,EPS,BPS,DPS,PER,PBR,발행주식수,배당수익률,영업활동현금흐름)
                        cursor.execute(replace_mysql, d)
                        conn.commit()

                if len(df_qtr.index) > 0:
                    기간구분 = '분기'
                    for idx, row in df_qtr.iterrows():
                        날짜, 매출액, 영업이익, 당기순이익, 자산총계, 부채총계, 자본총계, 자본금, 부채비율, 유보율, 영업이익률, 순이익률, ROA, ROE, EPS, BPS, DPS, PER, PBR, 발행주식수, 배당수익률,영업활동현금흐름 = row
                        종목코드 = code
                        d = (날짜,종목코드,기간구분,매출액,영업이익,당기순이익,자산총계,부채총계,자본총계,자본금,부채비율,유보율,영업이익률,순이익률,ROA,ROE,EPS,BPS,DPS,PER,PBR,발행주식수,배당수익률,영업활동현금흐름)
                        cursor.execute(replace_mysql, d)
                        conn.commit()

            time.sleep(2)
            cnt+=1

        except Exception as e:
            print(code, name, str(e))

    conn.close()


if __name__ == "__main__":
    build_fundamental_data()