import pandas as pd
import numpy as np

import ast
import re

from sqlalchemy import create_engine, text
from app.common.config import LocalConfig
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.conn import db
from app.database.schema import Stores, Users_prefer, Users
from models import PersonalModel_Item, PersonalModel_Detail_Item


router = APIRouter() 

# Change 가게 정보가 들어가는 곳
engine = create_engine(LocalConfig.DB_URL)
query_user = 'SELECT * FROM stores'
store_tb = pd.read_sql_query(sql=text(query_user), con=engine.connect())

store_tb['fix_menu'] = store_tb['menu']
store_tb['fix_menu'].apply(lambda x:re.sub(r'[\[\] ]','',x))
store_tb['fix_menu'] = store_tb['fix_menu'].apply(lambda x:ast.literal_eval(x))

def recommend_20s(sex,category,store_tb):
    from collections import Counter
    top_n =30
    recommeded_df = pd.DataFrame(columns=store_tb.columns)

    # 먼저 남/여가 선호한 식당에서
    if sex =='woman':
      filltered_store = store_tb[store_tb['20_woman']==True].sort_values(by=['view','point','star'],ascending=False).head(top_n)
    else:
      filltered_store = store_tb[store_tb['20_man']==True].sort_values(by=['view','point','star'],ascending=False).head(top_n)
       

    # 방문한 식당들의 음식들을 추출한다.
    favorite = filltered_store['fix_menu'].values.tolist()
    favorite =[item for sublist in favorite for item in sublist]
    favorite = [elm.strip()for elm in favorite]
    counter_list = Counter(favorite)

    # 음식들의 수가 많이 겹치는 것을 세고, 내림차순정렬
    sorted_list = counter_list.most_common()

    # 해당 성별이 좋아하는 음식의 누적된 갯수를 몇번째 랭킹까지 고려할것인가
    for i in range(5):
      temp = store_tb[store_tb['menu'].str.contains(sorted_list[i][0])]
      recommeded_df = recommeded_df.append(temp)
      recommeded_df[recommeded_df['category'].isin(category)]
      
    recommended_list = recommeded_df['store'].values.tolist()
    
    return recommended_list

@router.get('/boysandgirls', status_code=201, response_model=list[PersonalModel_Detail_Item])
async def boysandgirls(user_id : int, db : Session = Depends(db.session)):
    user_sex = db.query(Users).filter(Users.id == user_id).first().gender
    user_nickname = db.query(Users).filter(Users.id == user_id).first().nickname
    user_categories = db.query(Users_prefer).filter(Users_prefer.nickname == user_nickname).all()

    user_category = []
    for category in user_categories:
        if category.category != None:
            user_category.append(category.category)
            
    results = recommend_20s(user_sex, user_category, store_tb)
        
    final = []
    for result in results:
          final.append(db.query(Stores).filter(Stores.store == result).first())
    
    return final
    

# # Change DB 로부터 유저 정보를 받아오기

# # 유저 테이블로부터 성별 받아오기
# sex = 'woman'

# # 유저 테이블로부터 선호하는 카테고리 정보 받아오기
# category = ['까페','일식','양식']

# print(recommend_20s(sex,category,store_tb))