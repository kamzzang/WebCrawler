from urllib.request import urlopen
import requests
import datetime
import pandas as pd
import pandas.io.sql as pd_sql
import json
import telepot
import sqlite3

# OPENDART 고유번호 저장
from io import BytesIO
from zipfile import ZipFile
import xml.etree.ElementTree as ET

crtfc_key = '개인이 각자 받은 API인증키' # 자신의 API키를 넣어야 됨.

# 텔레그램 셋팅
token = 'XXXXXXXXXXXXXXXXXXXXXXXX' # 텔레그램 Bot 토큰
bot = telepot.Bot(token)
Bot_ID = 'XXXXXXX' # 수신자 ID

# 텔레그램 메세지 전송
def Sendmsg(msg):
    bot.sendMessage(Bot_ID, msg)

# OpenDART에 등록된 회사별 고유번호 저장 및 df 반환
def Get_Stocklist_by_DART():
    url = 'https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key={}'.format(crtfc_key)

    with urlopen(url) as zipresp:
        with ZipFile(BytesIO(zipresp.read())) as zfile:
            zfile.extractall('corpcode')

    tree = ET.parse('corpcode/CORPCODE.xml')
    root = tree.getroot()

    df_corp = pd.DataFrame(columns=['종목명', '고유번호', '종목코드'])
    for company in root.iter('list'):
        stock_code = company.findtext('stock_code')
        stock_code = stock_code.strip()

        if stock_code:
            data = {
                '종목명': company.findtext('corp_name'),
                '고유번호': company.findtext('corp_code'),
                '종목코드': company.findtext('stock_code')
            }

            df_corp = df_corp.append(data, ignore_index=True)

    df_corp = df_corp.sort_values(by='종목명')

    con = sqlite3.connect("DB.db")
    df_corp.to_sql('LIST', con, if_exists='append', index=False)
    con.close()

    return df_corp

# 기존 DB에 저장된 공시정보 읽음
def Check_Dart(stock):
    try:
        con = sqlite3.connect("DB.db")
        df = pd.read_sql("SELECT 보고서번호 from DART WHERE 종목명='%s'"%(stock), con=con)
        con.close()

        report_num = df['보고서번호'].tolist() # 저장된 공시의 보고서 번호만 리스트로 반환

        return report_num
    except Exception as e: # DART 테이블이 없거나 에러발생하면 빈 리스트를 반환
        print('Check_Dart Error : %s' %e)
        return []

# 신규 공시 DB저장
def DatatoSQL(df):

    con = sqlite3.connect("OpenDartBot.db")

    company = df['종목명'][0]
    sql = "DELETE FROM DART WHERE 종목명='%s'" % (company) # 해당 기업 데이터 삭제
    pd_sql.execute(sql, con)
    con.commit()

    df.to_sql('DART', con, if_exists='append', index=False) # 신규 데이터 저장
    con.close()

# API를 통한 공시 정보 수집
def Search_Dart(today, stock_list):
    # 금일 공시 정보만 받기 위해 마지막 날짜 변수 저장
    end_date = today.strftime("%Y%m%d")

    # 고유번호 dataframe
    con = sqlite3.connect("DB.db")
    df_corp = pd.read_sql('SELECT * from LIST', con=con)
    con.close()

    for stock in stock_list: # 관심 종목 list 하나씩 처리
        new_msg = False # 초기에 False 로 선언

        corp_code = df_corp[df_corp['종목명'] == stock]['고유번호'].values[0] # 회사명으로 고유번호 받아옴
        url = "https://opendart.fss.or.kr/api/list.json?crtfc_key=%s&corp_code=%s&end_de=%s&page_count=100" % (
            crtfc_key, corp_code, end_date)

        response = requests.get(url)
        data_json = json.loads(response.text)

        items = ['rcept_dt', 'corp_name', 'report_nm', 'rcept_no', 'flr_nm']
        cols = ['접수일자', '종목명', '보고서명', '보고서번호', '공시제출인명']
        link_base = 'http://m.dart.fss.or.kr/html_mdart/MD1007.html?rcpNo='
        result = []
        if data_json['status'] == '000':
            for data in data_json['list']:
                result.append([])
                for item in items:
                    if item in data.keys():
                        result[-1].append(data[item])
                    else:
                        result[-1].append('')

            df = pd.DataFrame(result, columns=cols)
            df['보고서링크'] = link_base + df['보고서번호']

            report_num = Check_Dart(stock)

            for num in df['보고서번호'].tolist():
                if num not in report_num: # 신규 정보 확인
                    new_msg = True

                    report = df[df['보고서번호'] == num]['보고서명'].values[0]
                    name = df[df['보고서번호'] == num]['공시제출인명'].values[0]
                    link = df[df['보고서번호'] == num]['보고서링크'].values[0]

                    print('[기업공시알림]\n%s\n%s\n제출 : %s\n%s' % (stock, report, name, link))
                    msg = '[기업공시알림]\n%s\n%s\n제출 : %s\n%s' % (stock, report, name, link)
                    Sendmsg(msg) # 텔레그램 메세지 전송

            if new_msg == True:
                DatatoSQL(df)
            else:
                print('%s : 신규 공시 없음' % (stock))

        else:
            print('%s : 데이터없음' % stock)

if __name__ == '__main__':
    current = datetime.datetime.now()
    current_time = current.strftime('%H:%M:%S')
    
    if current_time >= '07:00:00' and current_time <= '20:00:00': # 공시 업데이트되는 시간에 실행
        today = datetime.date.today() # 오늘 날짜 저장
        stock_list = ['삼성전자', 'SK하이닉스', '한화솔루션', 'LG화학'] # 원하는 종목을 리스트로 만듬
        Search_Dart(today, stock_list) # 공시 정보 수집 시작