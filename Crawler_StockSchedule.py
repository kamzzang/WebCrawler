from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
from html_table_parser import parser_functions as parser

url = 'http://www.38.co.kr/html/fund/index.htm?o=k'

data = urlopen(url).read()
soup = BeautifulSoup(data, 'html.parser')

table = soup.find("table", {'summary' : '공모주 청약일정'})

html_table = parser.make2d(table)

df=pd.DataFrame(html_table[2:], columns=html_table[0])
print(df)