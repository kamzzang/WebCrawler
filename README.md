# WebCrawler
> Web crawlers using Python
> 이 저장소는 파이썬을 이용한 웹크롤러와 텔레그램 봇을 제작한 코드들의 저장소입니다.

---
## 1. Cralwer_PublicHolidays.py
* 공공데이터 포털의 API를 이용한 공휴일 정보를 받아오는 크롤러
* 활용 : 자동화된 크롤러 중 주중에만 생성되는 데이터만  
         받아올 경우에 현재의 요일이 공휴일인지 확인
* [상세설명](https://blog.naver.com/kamzzang1/221432012754)

---
## 2. Cralwer_LottoResult.py
* 로또 최신 회차 결과 수집 및 DB 저장 크롤러
* 활용 : 로또 대박을 위한 기초 데이터 수집
* [상세설명](https://blog.naver.com/kamzzang1/221411622237)

---
## 3. Bot_StockMarketAnalysis.py
* 네이버의 코스피, 코스닥 지수를 이용하여 주식 시장의 현황을 텔레그램으로 전송하기 위한 크롤러  
  점수 계산 등은 아래 상세 설명 참조
* 활용 : 매일 아침 주식 시장 현황 확인을 위한 텔레그램 알람
* [상세설명](https://blog.naver.com/kamzzang1/221415304888)

---
## 4. Crawler_NaverSearch_API.py
* 네이버 검색 API를 활용한 크롤러, 예제로 경주 맛집에 대한 블로그와 지식인 검색한 결과를 csv로 저장함
* 활용 : 네이버 검색 결과 데이터 수집

---
## 5. Bot_SkiResortNotice.py
* 스키 시즌권 조기 구매를 위해서 스키리조트의 공지 게시판의 새로운 공지 알림을 확인하고 텔레그램으로 내용 전송
* 활용 : 관심있는 내용이 있는 인터넷 홈페이지의 게시판의 알림을 받아서 텔레그램으로 Bot 메시지 전송

---
## 6. Bot_JachiCenterNoticeSearch.py
* 주변 주민자치센터의 공지사항 알림을 전송받는 텔레그램 크롤러
* 활용 : 5번의 스키리조트 공지 게시판 공지 알림과 동일하게 공지 게시판의 신규 글 알림을 받아 텔레그램으로  Bot 메시지 전송

---
## 7. Bot_MaskStock.py
* 건강보험심사평가원_공적 마스크 판매 정보 Open API를 통해 관심 지역의 공적 마스크 현황 받아 텔레그램으로 내용 전송  
  https://www.data.go.kr/dataset/15043025/openapi.do
* 활용 : 매시간마다 실행되도록 하여 공적마스크 재고를 받아서 마스크 구매에 참고함
* [상세설명](https://blog.naver.com/kamzzang1/221901521374)

---
## 8. Crawler_StockCompanyReport.py
* 증권사 주식 추천 레포트 수집 크롤러
* 활용 : 매일 각 증권사의 추천주 레포트 수집, 일별 주가 정보와 함께 주가 동향 파악

---
## 9. Crawler_NaverMapsAPI_Geocoding.py
* 네이버 지도 API를 통한 경도 위도 변환
* 활용 : 데이터 분석 시 지도 시각화

---
## 10. Crawler_NaverPlaceSearch.py
* 네이버 검색 API를 활용한 크롤러로 네이버 플레이스 검색 결과 저장(예제 : 강동구 제로페이 가맹점 정보 수집)
* 활용 : 네이버 지역 검색 결과 수집

---
## 11. Cralwer_KatechCodeConvert.py
* 네이버 검색 API를 통해 수집된 장소의 좌표인 카텍 좌표를 WGS84로 변환
* 활용 : 네이버 지역 검색 결과를 활용한 지도 시각화

---
## 12. Crawler_StockSchedule.py
* 주식 공모주 청약 스케쥴 크롤링

---
## 13. Crawler_FinancialStatements.py
* 기업 재무제표 크롤링

---
## 14. Crawler_StockNews.py
* 관심 종목에 대한 네이버 증권사이트의 뉴스 크롤링
* 네이버 증권사이트의 주식 종목별 관련 뉴스를 받음
* 뉴스가 시간순으로 업데이트가 되지 않아 비효율적일 때가 있음

---
## 15. Crawler_OpenDartAPI.py
* 전자공시시스템 API(Opendart)를 이용한 공시 정보 크롤링

---
## 16. Bot_OpenDartDataNotice.py
* 전자공시시스템 API(Opendart)를 이용한 공시정보 텔레그램 봇
* 관심 종목 설정 후 해당 종목에 대한 전자공시 내용을 텔레그램을 통한 알림받기
* 매일 주중 알림을 위해서 당일 공시만 받음
* 매년 초에 해당연도의 공휴일 정보 받아 저장, 공휴일이 아닌 주중에 실행되도록 
* [상세설명](https://blog.naver.com/kamzzang1/222166180806)
