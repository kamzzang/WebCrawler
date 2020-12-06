from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd


# 종목코드 0제외된 코드 수정
def Fix_stockcode(data):
    data = str(data)
    if len(data) < 6:
        for i in range(6 - len(data)):
            data = '0' + data
    return data

# KRX 종목 리스트 저장
def Get_Stocklist():
    df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)[0]
    df['종목코드'] = df['종목코드'].apply(Fix_stockcode)
    df = df[['회사명', '종목코드']].sort_values(by='회사명')

    return df

# 신규 뉴스 확인
def Search_News(df, Stocklist):
    for company in Stocklist:
        code = df[df['회사명'] == company]['종목코드'].values[0]
        print(company, code)

        url = 'https://finance.naver.com/item/news_news.nhn?code=%s&page=1' % (code)
        html = urlopen(url).read()
        soup = BeautifulSoup(html, 'html.parser')

        # 뉴스 제목, 링크
        title_new = []
        link_new = []
        titles = soup.findAll('td', class_='title')
        for i in titles:
            title_new.append(i.text.replace('\n', ''))
            link_new.append('https://finance.naver.com' + i.find('a')['href'])

        # 날짜
        dates = soup.select('.date')
        date_new = [date.get_text() for date in dates]

        # 매체
        sources = soup.select('.info')
        source_new = [source.get_text() for source in sources]

        for date, source, title, link in zip(date_new, source_new, title_new, link_new):
            print('[기업뉴스]\n%s\n%s\t%s\n%s\n%s' % (company, source, date, title, link))


if __name__ == '__main__':
    Stocklist = ['삼성전자', '현대자동차', '카카오']
    df_list = Get_Stocklist()
    Search_News(df_list, Stocklist)
