from selenium import webdriver # 가상 드라이버 구동을 위한 모듈
from selenium.webdriver.common.keys import Keys # 키보드 버튼을 제어하기 위한 모듈

import time # 딜레이를 위한 time 모듈

import pyperclip # 클립보드에 복사

# 네이버 홈페이지
url = 'https://www.naver.com'

# 크롬드라이버를 웹드라이버로 띄움
driver = webdriver.Chrome('chromedriver.exe')
driver.get(url) # URL로 드라이버 연결

# class가 link_login인 '네이버로그인'버튼 클릭
driver.find_element_by_class_name('link_login').click()
time.sleep(1) # 1초 딜레이

# id가 id인 아이디 입력 부분 저장
input_id = driver.find_element_by_id('id')
input_id.click() # 입력 부분 클릭
pyperclip.copy('Your ID') # 아이디에 입력할 값을 복사
input_id.send_keys(Keys.CONTROL, 'v') # ctrl + v 입력 : 붙여넣기
time.sleep(1) # 1초 딜레이

# id가 pq인 비밀번호 입력 부분 저장
input_pw = driver.find_element_by_id('pw')
input_pw.click() # 입력 부분 클릭
pyperclip.copy('Your Password') # 비밀번호에 입력할 값을 복사
input_pw.send_keys(Keys.CONTROL, 'v') # ctrl + v 입력 : 붙여넣기
time.sleep(1) # 1초 딜레이

# id가 log.login인 로그인 버튼 클릭
driver.find_element_by_id('log.login').click()