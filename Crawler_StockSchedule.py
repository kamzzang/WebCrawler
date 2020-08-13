from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
from html_table_parser import parser_functions as parser

import telepot
import datetime
import sqlite3
import pandas.io.sql as pd_sql

token = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
bot = telepot.Bot(token)

today = datetime.datetime.now().strftime('%Y.%m.%d')

def DatatoSQL(df):
    con = sqlite3.connect("StockSchedule.db")

    cursor = con.cursor()
    cursor.execute('DELETE FROM 공모주일정')
    con.commit()

    df.to_sql('공모주일정', con, if_exists='append', index=False)
    con.close()

def Check():
    try:
        con = sqlite3.connect("StockSchedule.db")

        df = pd.read_sql('select * from 공모주일정 ORDER BY 일정 ASC', con=con)
        con.close()

        stock = list(df['종목명'].values)
        date = list(df['일정'].values)
    except:
        print('DB 데이터 에러')
        stock = []
        date = []

    return stock, date

def Search():
    url = 'http://www.38.co.kr/html/fund/index.htm?o=k'

    data = urlopen(url).read()
    soup = BeautifulSoup(data, 'html.parser')

    table = soup.find("table", {'summary': '공모주 청약일정'})
    html_table = parser.make2d(table)

    df = pd.DataFrame(html_table[2:], columns=html_table[0])
    df['일정'] = df['공모주일정'].str[:10]
    df = df[df['일정'] >= today].sort_values(by='일정', ascending=True)
    df = df[['종목명', '일정', '공모주일정', '희망공모가', '주간사']].reset_index(drop=True)

    stock_new = list(df['종목명'].values)
    date_new = list(df['일정'].values)
    price_new = list(df['희망공모가'].values)
    company_new = list(df['주간사'].values)
    print(df)

    stock_old, date_old = Check()

    num = 1
    msg = []
    new_msg = False
    for date, stock, price, company in zip(date_new, stock_new, price_new, company_new):
        if (date not in date_old) and (stock not in stock_old):
            new_msg = True
            msg.append(str(num) + '. ' + stock + ' / ' + date + ' / ' + price + ' / ' + company + '\n\n')
        num += 1
    if new_msg == True:
        msg.append(url)
        msg_final = "".join(msg)  # 리스트 내부 인자들을 전부 합치기. ""안에 기호를 넣으면 기호 포함되어 합쳐짐
        bot.sendMessage(12345678, "<신규 공모주 청약 일정>" + "\n" + msg_final)

        # DB 저장
        DatatoSQL(df)
    else:
        print('신규 일정 없음')

if __name__ == '__main__':
    Search()


