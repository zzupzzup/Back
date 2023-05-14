import sys
import os
import pandas as pd
import numpy as np

import build_matrix as bm
import CF_recommend as cf_r

from fastapi import APIRouter, Depends
from sqlalchemy import create_engine, text
from app.common.config import LocalConfig

from sqlalchemy.orm import Session
from app.database.conn import db
from app.database.schema import Users, Stores
from starlette.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from models import PersonalModel_Item, PersonalModel_Detail_Item

router = APIRouter()

#personalModel 결과 추천
@router.get('/personalModel',  status_code=201, response_model=list[PersonalModel_Item])
async def personalModel(db : Session = Depends(db.session)) :
    
    engine = create_engine(LocalConfig.DB_URL)
    query_user = 'SELECT * FROM users_for_personalModel'
    query_store = 'SELECT * FROM stores'

    user_tb = pd.read_sql_query(sql=text(query_user), con=engine.connect())
    store_tb = pd.read_sql_query(sql=text(query_store), con=engine.connect())

    threshold_user = user_tb[user_tb['nickname'].map(user_tb['nickname'].value_counts()) > 1]
    #new_user = [input("새로운 유저 입력: ")]
    new_user = [db.query(Users).order_by(Users.id.desc()).first().nickname] # 입력값이 '승현'일 때 안됨 이슈
    
    
    # 기존에 있는 유저들
    mask = threshold_user['nickname'].isin(new_user)
    filtered_user = threshold_user[~mask]
    users = filtered_user.drop(filtered_user[filtered_user['nickname'].isin(new_user)].index)


    #import IPython; IPython.embed(colors="Linux"); exit(1)

    # 새로운 유저들
    new_users = threshold_user[threshold_user['nickname'].isin(new_user)]

    users_df = bm.merge_store_table(users,store_tb)
    new_users_df = bm.merge_store_table(new_users,store_tb)

    # users + new_users
    concated_df = pd.concat([users_df,new_users_df],ignore_index=True)

    pv_table = bm.make_pivot_table(concated_df)
    cs_table = bm.calculate_cosine_similarity(pv_table)

    select_top_n_user = 5 # args
    similar_user = cf_r.search_simular_user(cs_table,new_user,select_top_n_user)

    sort_table = cf_r.calculate_food_type(pv_table,new_user,similar_user)

    select_n =5

    results= cf_r.cf_recommend(sort_table,store_tb,select_n)
    
    final =[]
    for result in results:
        final.append(db.query(Stores).filter(Stores.store == result).first())
    
    if len(results) == 0 :
        return JSONResponse(status_code=404, content=dict(msg="NO_RESULTS"))
    return final

#personalModel 상세페이지 store 정보 전달
@router.get('/personalModel/detail/{store}',  status_code=201, response_model=PersonalModel_Detail_Item)
async def personalModel_detail(store : str, db : Session = Depends(db.session)) :
    return db.query(Stores).filter(Stores.store == store).first()
