import time
import telepot
from _datetime import datetime
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from pandas import DataFrame
from selenium import webdriver
import json
import os

admin_info_file = os.getenv('APPLICATION_ADMIN_INFO') # 환경 변수에 저장한 중요 개인 정보 불러옴
with open(admin_info_file, 'r') as f:
    admin_info = json.load(f)

token = admin_info['telegram']['token'] # "Individual Telegram Token"
Bot_ID = admin_info['telegram']['id']['mc'] # "Receiver's Telegram ID"

def Search_Daily(stock, term):
    web = webdriver.Chrome('chromedriver.exe')  # 크롬 웹 드라이버(본 py파일과 동일위치에 파일이 있을 경우는 별도 경로 불필요)

    url = 'https://m.stock.naver.com/sise/siseIndex.nhn?code=%s' % (stock)

    web.get(url)
    time.sleep(3)  # 데이터가 화면에 완전히 뜰 수 있도록 기다림
    html_source = web.page_source
    web.close()  # 크롬 웹드라이버 닫음

    soup = BeautifulSoup(html_source, 'html.parser')

    table = soup.find_all('td', class_='_child_wrapper')

    cnt = 0  # 받은 데이터 자리 확인용(날짜, 종가)
    date = []
    close = []

    df = DataFrame()
    dt = datetime.now()  # 날짜 오류 방지를 위해 현재 날짜받아옴

    for i in table:

        if cnt == 0 or cnt % 7 == 0:  # 날짜 저장(0번과 7의 배수자리이므로 7을 나눠서 나머지가 0인 자리)
            if dt.month < 5:  # 오늘이 5월 이전일 경우
                if i.text[:2] == '01':  # 1월 데이터면 올해 데이터
                    date.append(str(dt.year) + '-' + (i.text).replace('.', '-'))
                elif i.text[:2] == '02':  # 2월 데이터면 올해 데이터
                    date.append(str(dt.year) + '-' + (i.text).replace('.', '-'))
                elif i.text[:2] == '03':  # 3월 데이터면 올해 데이터
                    date.append(str(dt.year) + '-' + (i.text).replace('.', '-'))
                elif i.text[:2] == '04':  # 4월 데이터면 올해 데이터
                    date.append(str(dt.year) + '-' + (i.text).replace('.', '-'))
                else:  # 모두 아닐 경우는 작년데이터로 처리
                    date.append(str(dt.year - 1) + '-' + (i.text).replace('.', '-'))
            else:
                date.append(str(dt.year) + '-' + (i.text).replace('.', '-'))
        elif cnt == 1 or (cnt - 1) % 7 == 0:  # 종가 저장(1번과 6의 배수자리)
            close.append((i.text).replace(',', ''))

        cnt += 1

    df['DATE'] = date
    df['CLOSE'] = close

    df['CLOSE'] = pd.to_numeric(df['CLOSE'])  # 게산을 위해서 숫자형으로 변환

    df = df[['DATE', 'CLOSE']]
    df = df.sort_values(by='DATE')
    df = df.set_index('DATE', inplace=False)

    df['MA3'] = df['CLOSE'].rolling(window=3).mean()  # 종가 3일 평균 열 생성
    df['MA5'] = df['CLOSE'].rolling(window=5).mean()  # 종가 5일 평균 열 생성
    df['MA10'] = df['CLOSE'].rolling(window=10).mean()  # 종가 10일 평균 열 생성
    df['MA20'] = df['CLOSE'].rolling(window=20).mean()  # 종가 20일 평균 열 생성
    df['SUM1'] = np.where(df['CLOSE'] - df['MA3'] > 0, 1, 0)  # 종가 > 3일 평균이면 1점, 아니면 0점 부여
    df['SUM2'] = np.where(df['CLOSE'] - df['MA5'] > 0, 1, 0)  # 종가 > 5일 평균이면 1점, 아니면 0점 부여
    df['SUM3'] = np.where(df['CLOSE'] - df['MA10'] > 0, 1, 0)  # 종가 > 10일 평균이면 1점, 아니면 0점 부여
    df['SUM4'] = np.where(df['CLOSE'] - df['MA20'] > 0, 1, 0)  # 종가 > 20일 평균이면 1점, 아니면 0점 부여
    df['SUM'] = df['SUM1'] + df['SUM2'] + df['SUM3'] + df['SUM4']  # 부여 점수 합 계산

    score = 0
    for i in range(1, term + 1):
        score = np.where(df['CLOSE'] / df['CLOSE'].shift(i) > 1, 1,0) + score  # 마지막 날 기준으로 1일전 ~ 20일전까지 일별 비교하여 높으면 1, 낮으면 0으로 스코어 매겨서 더함
    score = str(score[len(score) - 1] / term * 100)  # 기간으로 나눠서 평균모멘텀 게산함

    result = str(df['SUM'][len(df) - 1])
    return score, result


if __name__ == '__main__':
    stock = ['KOSPI', 'KOSDAQ']
    term = 20  # 기간은 임의 지정
    Result_data = []

    for i in stock:
        score, result = Search_Daily(i, term)
        Result_data.append(score)
        Result_data.append(result)

    # 결과 텔레그램 전송
    bot = telepot.Bot(token)
    bot.sendMessage(Bot_ID, '<주가지수모멘텀>' + '\n' + '1. 20일 평균 모멘텀' + '\n\t\t\t\t' \
                    + stock[0] + ' : ' + Result_data[0] + '%' + '\n\t\t\t\t' + stock[1] + ' : ' + Result_data[2] + '%' + '\n' \
                    + '2. 이동평균 모멘텀(4점)' + '\n\t\t\t\t' + stock[0] + ' : ' + Result_data[1] + '\n\t\t\t\t' + stock[1] + ' : ' + Result_data[3])