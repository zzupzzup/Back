import sys
import os
import pandas as pd
import numpy as np

import build_matrix as bm
import CF_recommend as cf_r

from fastapi import APIRouter, Depends, Header
from sqlalchemy import create_engine, text
from app.common.config import LocalConfig

from sqlalchemy.orm import Session
from app.database.conn import db
from app.database.schema import Users, Stores
from starlette.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from models import PersonalModel_Item, PersonalModel_Detail_Item

router = APIRouter()



@router.get('/personalModel',  status_code=201, response_model=list[PersonalModel_Item]) 
async def personalModel(token : str = Header(default=None), db : Session = Depends(db.session)) :

    engine = create_engine(LocalConfig.DB_URL)
    query_user = 'SELECT * FROM users_for_personalModel'
    query_store = 'SELECT * FROM stores'

    user_tb = pd.read_sql_query(sql=text(query_user), con=engine.connect())
    store_tb = pd.read_sql_query(sql=text(query_store), con=engine.connect())

    args = {
        #  어느정도 식당을 방문한 유저의 데이터를 고려할 것인지
        'n_value_counts':5,

        #   몇명의 비슷한 유저를 고려할 것인지
        'select_top_n_user':20,

        #   몇개의 식당을 순차적으로 뽑을 것인지
        'select_n_sotre':25
    }


    threshold_user = user_tb[user_tb['nickname'].map(user_tb['nickname'].value_counts()) > args['n_value_counts']]
    new_user = [db.query(Users).filter(Users.token == token).first().nickname]
    #new_user = [db.query(Users).order_by(Users.id.desc()).first().nickname]


    # 기존에 있는 유저들
    mask = threshold_user['nickname'].isin(new_user)
    filtered_user = threshold_user[~mask]
    users = filtered_user.drop(filtered_user[filtered_user['nickname'].isin(new_user)].index)

    # 새로운 유저들
    # new_users = threshold_user[threshold_user['nickname'].isin(new_user)]
    new_users = user_tb[user_tb['nickname'].isin(new_user)]

    # new_users

    users_df = bm.merge_store_table(users,store_tb)
    # users_df
    new_users_df = bm.merge_store_table(new_users,store_tb)
    # new_users_df
    # users + new_users
    concated_df = pd.concat([users_df,new_users_df],ignore_index=True)
    # concated_df


    pv_table = bm.make_pivot_table(concated_df)
    # pv_table
    cs_table = bm.calculate_cosine_similarity(pv_table)
    cs_table

    # select_top_n_user = 10 # args
    similar_user = cf_r.search_simular_user(cs_table,new_user,args['select_top_n_user'])
    # similar_user

    sort_table = cf_r.calculate_food_type(pv_table,new_user,similar_user)
    # sort_table

    #select_n =5

    results= cf_r.cf_recommend(sort_table,store_tb,args['select_n_sotre'])
    results
    # print('유저가 좋아할만한 음식분야에서 인기가 있는 식당들을 추출한 것')
    # print(result)
    # print(store_tb[store_tb['title'].isin(result)]['업태명'].value_counts())

    #similar_store =  cf_r.cf_recommend_b(similar_user, user_tb,store_tb)
    # print('\n사용자와 비슷한 성향을 가진 사람들이 공통적으로 가는 식당들을 추출한 것')
    # print(similar_store)
    # print(store_tb[store_tb['title'].isin(similar_store)]['업태명'].value_counts())


    #similar_food = cf_r.cf_recommend_c(store_tb,user_tb,new_user)
    #similar_food
    # print('\n유저가 좋아할만한 음식을 파는 식당을 추출한 것')
    # print(similar_food)
    # print(store_tb[store_tb['title'].isin(similar_food)]['업태명'].value_counts())
    
    final =[]
    for result in results:
        final.append(db.query(Stores).filter(Stores.store == result).first())
    
    return final

# #personalModel 상세페이지 store 정보 전달
# @router.get('/personalModel/detail/{id}',  status_code=201, response_model=PersonalModel_Detail_Item)
# async def personalModel_detail(id : int, db : Session = Depends(db.session)) :
#     store = db.query(Stores).filter(Stores.id == id ).first().store
#     return db.query(Stores).filter(Stores.store == store).first()



#personalModel 결과 추천
# @router.get('/personalModel',  status_code=201, response_model=list[PersonalModel_Item]) 
# async def personalModel(db : Session = Depends(db.session)) :
    
#     engine = create_engine(LocalConfig.DB_URL)
#     query_user = 'SELECT * FROM users_for_personalModel'
#     query_store = 'SELECT * FROM stores'

#     user_tb = pd.read_sql_query(sql=text(query_user), con=engine.connect())
#     store_tb = pd.read_sql_query(sql=text(query_store), con=engine.connect())

#     threshold_user = user_tb[user_tb['nickname'].map(user_tb['nickname'].value_counts()) > 1]
#     #new_user = [input("새로운 유저 입력: ")]
#     new_user = [db.query(Users).order_by(Users.id.desc()).first().nickname] # 입력값이 '승현'일 때 안됨 이슈
    
    
#     # 기존에 있는 유저들
#     mask = threshold_user['nickname'].isin(new_user)
#     filtered_user = threshold_user[~mask]
#     users = filtered_user.drop(filtered_user[filtered_user['nickname'].isin(new_user)].index)

#     # 새로운 유저들
#     new_users = user_tb[user_tb['nickname'].isin(new_user)]

#     users_df = bm.merge_store_table(users,store_tb)
#     new_users_df = bm.merge_store_table(new_users,store_tb)

#     # users + new_users
#     concated_df = pd.concat([users_df,new_users_df],ignore_index=True)

#     pv_table = bm.make_pivot_table(concated_df)
#     cs_table = bm.calculate_cosine_similarity(pv_table)

#     select_top_n_user = 5 # args
#     similar_user = cf_r.search_simular_user(cs_table,new_user,select_top_n_user)

#     sort_table = cf_r.calculate_food_type(pv_table,new_user,similar_user)

#     select_n =5

#     results = cf_r.cf_recommend(sort_table,store_tb,select_n)
    
#     final =[]
#     for result in cf_r.cf_recommend(sort_table,store_tb,select_n):
#         final.append(db.query(Stores).filter(Stores.store == result).first())
        
    
#     if len(results) == 0 :
#         return JSONResponse(status_code=404, content=dict(msg="NO_RESULTS"))
    
#     return final