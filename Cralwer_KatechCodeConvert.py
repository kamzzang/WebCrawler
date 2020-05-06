import pandas as pd
import json

df = pd.read_csv('D:/설계효율화Tool/Python/Flask/pybotserver/data/zmoney_gangdong.csv', encoding='euc-kr')

x = list(df['X'].values)
y = list(df['Y'].values)

lng=[]
lat=[]

for i in range(len(x)):
    url = 'https://dapi.kakao.com/v2/local/geo/transcoord.json?x=%s&y=%s&input_coord=KTM&output_coord=WGS84'%(str(x[i]), str(y[i]))
    headers = {"Authorization": "KakaoAK XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"}
    result = json.loads(str(requests.get(url,headers=headers).text))

    if len(result['documents']) !=0:
        lng.append(result['documents'][0]['x'])
        lat.append(result['documents'][0]['y'])
    else:
        lng.append(None)
        lat.append(None)
        
df['경도'] = lng
df['위도'] = lat

df.head()