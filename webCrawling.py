# -*- coding: utf-8 -*-
""""
올리브영 공식 온라인몰 사이트에서 20개 베스트 상품 정보 저장(판매랭킹)
"""

from urllib.request import urlopen # 함수 : 원격서버 url 요청  
from bs4 import BeautifulSoup # 클래스 : html 파싱 

# 올리브영 공식 온라인몰 사이트
url = 'https://www.oliveyoung.co.kr/store/main/getBestList.do'

# 1. 원격 서버 url 요청 
req = urlopen(url)  # ulr 요청 
byte_data = req.read() # data 읽기   
print(byte_data)

# 2. html 파싱 
text_data = byte_data.decode("utf-8") # 디코딩 : charset="utf-8" 
print(text_data)
html = BeautifulSoup(text_data, 'html.parser') # html source 파싱
print(html)
                                                                                                                                                                                                                  
# 3. 베스트 상품 정보 20개 element 수집
product_list1 = html.select('div[class="TabsConts on"] > ul[class="cate_prd_list"] >li')
print(product_list1)
len(product_list1) # 베스트 상품 4개 수집

product_list2 = html.select('div[class="TabsConts on"] > ul[class="cate_prd_list mgLine"] >li', limit=16)
print(product_list2)
len(product_list2)

product_list = product_list1 + product_list2
product_list
len(product_list) # 20개

# 4. a태그의 href 속성 수집
urls = []
for li in product_list:
    a_tag = li.select_one('div[class="prd_info"] > a')
    urls.append(a_tag.get('href')) 

print(urls)						
len(urls)# 20
urls[0] 
# 'https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000163539&dispCatNo&trackingCd=Best_Sellingbest&curation&egcode&rccode&egrankcode'
urls[-1]								
# 'https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000147617&dispCatNo&trackingCd=Best_Sellingbest&curation&egcode&rccode&egrankcode'


def crawler(url) : # 자료수집 함수 
    print('url :', url)
    # 1. url 요청 
    req = urlopen(url)  # ulr 요청 
    byte_data = req.read() # data 읽기  
    # 2. 디코딩 
    text_data = byte_data.decode("utf-8")    
    # 3. html 파싱
    html = BeautifulSoup(text_data, 'html.parser')    
    # 4. tag & 내용 수집
    brand = html.select_one('div[class = "prd_info"] > p[class="prd_brand"] > a').string
    detail = html.select_one('div[class = "prd_info"] > p[class="prd_name"]').string
    
    return [brand, detail] 
    
# 함수호출
product_contents = [crawler(url) for url in urls]
len(product_contents)  # 20
product_contents

    
# 6. DataFrame -> csv file 저장
import pandas as pd  # DataFrame

product_df = pd.DataFrame(product_contents, columns=['brand', 'detail'])
product_df.info()
'''
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 20 entries, 0 to 19
Data columns (total 2 columns):
 #   Column  Non-Null Count  Dtype 
---  ------  --------------  ----- 
 0   brand   20 non-null     object
 1   detail  20 non-null     object
dtypes: object(2)
memory usage: 448.0+ bytes
'''

print(product_df)

path = r'/Users/yingying/ITWILL/4_Python-I/workspace/chap10_Crawling/data'  
product_df.to_csv(path + '/product_df.csv', index = None)

for row in product_df.itertuples():
    print(type(row[0]))

####################################################
import pymysql
config = {
    'host' : '127.0.0.1',
    'user' : 'scott',
    'password' : 'tiger',
    'database' : 'work',
    'port' : 3306,
    'charset':'utf8',
    'use_unicode' : True}

try :
    # 1. db 연동 객체 생성 
    conn = pymysql.connect(**config) # 환경변수 이용
    # 2. sql문 실행 객체 
    cursor = conn.cursor()   # object.method() 
    
    # 3. table 유무 판단 : product_df 
    cursor.execute("show tables") # table 목록 조회 
    tables = cursor.fetchall() # table 목록 가져오기 

    # product_df 테이블 조회 
    sw = False # off
    for table in tables : 
        if 'product_df' in table :
            sw = True # on

    # 2. 레코드 조회/추가 or table 생성         
    if sw : # table 있는 경우        
        query = "select * from product_df"
        cursor.execute(query)
        dataset = cursor.fetchall()
        
        if dataset : # 1) 레코드 있는 경우 : 조회 
            select = int(input('~~브랜드로 찾으려면 1번, 상품내용으로 찾으려면 2번을 입력하십시오:'))
            if select == 1:
                brand = input('브랜드명을 입력하십시오:')
                cursor.execute(f"select * from product_df where brand like '%{brand}%'")
            if select == 2:
                detail = input('상품내용을 입력하십시오:')
                cursor.execute(f"select * from product_df where detail like '%{detail}%'")
            result = cursor.fetchall()
            if result:
                for i in result:
                    print(i)
            else:
                print('해당 상품은 없습니다.')                
        else : # 2) 레코드 없는 경우 : 추가 
            print('레코드 추가')
            for row in product_df.itertuples():
                cursor.execute(f"insert into product_df(brand, detail) values ('{row[1]}', '{row[2]}')")
            conn.commit() # db 반영

    else : # table 없는 경우                 
        print('테이블 생성') 
        query = """create or replace table product_df(
        brand varchar(50) not null,
        detail varchar(500) not null)"""

        cursor.execute(query) # table 생성 (commit 불필요)
        print('~~ product_df table 생성 완료 ~~')
   
except Exception as e :
    print('db error : ', e)
finally :
    cursor.close(); conn.close() # 객체 닫기: 역순


