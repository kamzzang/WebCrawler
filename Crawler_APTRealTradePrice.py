import pandas as pd
import urllib.request
from bs4 import BeautifulSoup

def GetAddCode(address):
    df_code = pd.read_csv('법정동코드 전체자료.txt', sep='\t', encoding='euc-kr')
    df_code = df_code[df_code['폐지여부'] == '존재']
    df_code = df_code[['법정동코드', '법정동명']]

    code = str(df_code.loc[(df_code['법정동명'].str.contains(address.split(' ')[0])) & (df_code['법정동명'].str.contains(address.split(' ')[1]))]['법정동코드'].values[0])[:5]

    return code

def GetData(address, period):
    address_code = GetAddCode(address)

    servicekey = '일반 인증키 입력'

    url = f'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTrade?LAWD_CD={address_code}&DEAL_YMD={period}&serviceKey={servicekey}'
    f = urllib.request.urlopen(url)
    aptdatas = f.read().decode('utf8')
    f.close()

    soup = BeautifulSoup(aptdatas, 'lxml')

    aptdata = list(aptdata.get_text().replace('\n', '').split('>') for aptdata in soup.find_all('item'))

    data_cols = ['거래금액', '건축년도', '년', '법정동', '아파트', '월', '일', '전용면적', '지번', '지역코드', '층']
    final = {'년': [],
             '월': [],
             '일': [],
             '법정동': [],
             '지번': [],
             '아파트': [],
             '건축년도': [],
             '전용면적': [],
             '층': [],
             '거래금액': []}

    for data in aptdata:
        for i in data_cols:
            if i != '지역코드':
                final[i].append(data[data_cols.index(i)][:-len(i)].strip())

    df = pd.DataFrame(final)
    df_result = df.loc[df['법정동'].str.contains(address.split(' ')[1])]
    df_result.reset_index(drop=True, inplace=True)
    return df_result

if __name__ == '__main__':
    address = '용인 죽전'
    period = '202012'
    result = GetData(address, period)
    print(result)
