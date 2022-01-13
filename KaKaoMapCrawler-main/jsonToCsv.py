import pandas as pd
import json

#### csv 파일로 만들 txt파일명
with open('data//kakao1019_260개.json', encoding='utf-8') as f:
    data = f.readlines()
    data = [json.loads(line) for line in data]

df = pd.DataFrame(data)
### csv파일 이름 설정
df.to_csv('data//test_gimcheon.csv', index=False)

