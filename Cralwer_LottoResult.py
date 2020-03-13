import pandas as pd
import sqlite3
import requests
from bs4 import BeautifulSoup

# 마지막 회차 확인 주소
main_url = "https://www.dhlottery.co.kr/gameResult.do?method=byWin"

# 회차별 당첨 정보 주소
basic_url = "https://www.dhlottery.co.kr/gameResult.do?method=byWin&drwNo="

# 마지막 회차 확인 함수
def GetLast():
    resp = requests.get(main_url)
    soup = BeautifulSoup(resp.text, "lxml")
    result = str(soup.find("meta", {"id" : "desc", "name" : "description"})['content']) # meta 태그에서 id 속성이 desc이고 name 속성이 description인 태그를 찾아 content를 string으로 result에 저장

    s_idx = result.find(" ") # 1. 회차 앞에 공란이 있고
    e_idx = result.find("회") # 2. 회차 다음에 '회'가 나오기 때문에

    return int(result[s_idx + 1 : e_idx]) # 3. 공란 다음부터 '회'이전까지가 마지막 회차이며 이것을 integer로 변환하여 리턴한다.

# 입력한 여러 회차 정보 크롤링 함수
def Crawler(s_count, e_count):
    for i in range(s_count , e_count + 1):
        print(str(i) + "회차 크롤링")
        crawler_url = basic_url + str(i)

        resp = requests.get(crawler_url)
        soup = BeautifulSoup(resp.text, "lxml")
        result = str(soup.find("meta", {"id": "desc", "name": "description"})['content'])
        # result : 동행복권 835회 당첨번호 9,10,13,28,38,45+35. 1등 총 15명, 1인당 당첨금액 1,233,681,125원.

        s_idx = result.find("당첨번호")
        s_idx = result.find(" ", s_idx) + 1 # find() 함수 : string.find(search, start, end)
        e_idx = result.find(".", s_idx)
        numbers = result[s_idx:e_idx]

        s_idx = result.find("총")
        s_idx = result.find(" ", s_idx) + 1
        e_idx = result.find("명", s_idx)
        persons = result[s_idx:e_idx]

        s_idx = result.find("당첨금액")
        s_idx = result.find(" ", s_idx) + 1
        e_idx = result.find("원", s_idx)
        price = result[s_idx:e_idx]

        info = {}  # 당첨정보 저장 Dictionary
        info["회차"] = i
        info["당첨번호"] = numbers
        info["당첨자수"] = persons
        info["당첨금액"] = price

        lotto_list.append(info) # 결과 저장 리스트에 추가

def DatatoDB():
    print("DATA 저장")
    df = pd.DataFrame()
    count = []
    num1 = []
    num2 = []
    num3 = []
    num4 = []
    num5 = []
    num6 = []
    num7 = []
    persons = []
    price = []

    con = sqlite3.connect("Lotto.db")

    for i in lotto_list:
        count = i["회차"]
        numbers = i["당첨번호"]
        persons = i["당첨자수"]
        price = i["당첨금액"]

        numberlist = str(numbers).split(",")

        sql = "INSERT INTO `회차별_당첨정보`(`회차`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `당첨자수`, `당첨금액`) " \
              "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        data = (count,
                int(numberlist[0]),
                int(numberlist[1]),
                int(numberlist[2]),
                int(numberlist[3]),
                int(numberlist[4]),
                int(numberlist[5].split("+")[0]),
                int(numberlist[5].split("+")[1]),
                int(persons),
                str(price))
        cur = con.cursor()
        cur.execute(sql,data)
        con.commit()

        # 중복데이터 제거
        sql = "DELETE FROM `회차별_당첨정보` WHERE rowid NOT IN  (SELECT Max(rowid) FROM `회차별_당첨정보` GROUP BY 회차 order by 회차)"
        cur.execute(sql)
        con.commit()

    con.close()

lotto_list = [] # 웹 크롤링 한 결과를 저장할 리스트

last = GetLast() # 최신 회차 받기
Crawler(last-10,last) # 최신 회차 이전 10회의 결과 크롤링
DatatoDB() # 저장된 모든 정보를 DB에 저장