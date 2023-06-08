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
from app.database.schema import Users, Stores, Users_prefer, Users_like
from starlette.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from models import PersonalModel_Item, PersonalModel_Detail_Item
from typing import Optional
import ast
router = APIRouter()

@router.get('/personalModel',  status_code=201) # 
async def personalModel(user_id : int, db : Session = Depends(db.session)) :
    user_nickname = db.query(Users).filter(Users.id == user_id).first().nickname

    engine = create_engine(LocalConfig.DB_URL)
    query_user = 'SELECT * FROM users_for_personalModel'
    query_store = 'SELECT * FROM stores'
    query_user_like = 'SELECT * FROM users_like'
    query_user_prefer = 'SELECT * FROM users_prefer'

    user_tb = pd.read_sql_query(sql=text(query_user), con=engine.connect())
    store_tb = pd.read_sql_query(sql=text(query_store), con=engine.connect())
    pos_df = pd.read_sql_query(sql=text(query_user_like), con=engine.connect())
    user_clicked = pd.read_sql_query(sql=text(query_user_prefer), con=engine.connect())
    

    store_tb = store_tb.rename(columns={'menu':'주된음식'})
    store_tb['search_food'] = store_tb['주된음식']
    store_tb['주된음식'] = store_tb['주된음식'].apply(ast.literal_eval)



    args = {
        #  어느정도 식당을 방문한 유저의 데이터를 고려할 것인지
        'n_value_counts':5,

        #   몇명의 비슷한 유저를 고려할 것인지
        'select_top_n_user':20,

        #   몇개의 식당을 순차적으로 뽑을 것인지
        'select_n_sotre':25
    }


    threshold_user = user_tb[user_tb['nickname'].map(user_tb['nickname'].value_counts()) > args['n_value_counts']]

    users = threshold_user

    user_clicked = user_clicked[['nickname','store']]

    # 새로운 유저를 new_user에 넣음
    new_user= db.query(Users).filter(Users.id==user_id).first().nickname
    new_users = user_clicked[user_clicked['nickname']==new_user]
    new_users = new_users.dropna(subset=['store'])
    pos_df = pos_df[pos_df['nickname']==new_user]

    users_df = bm.merge_store_table(users,store_tb)
    new_users_df = bm.merge_store_table(new_users,store_tb)

    store2category ={}
    for idx in range(len(store_tb)):
        store2category[store_tb.loc[idx,'store']]=store_tb.loc[idx,'category']


    value_count= pos_df['store'].value_counts()
    value_count = value_count[value_count%2!=0]

    value_count_dic = value_count.to_dict()

    pos_dic ={}
    for elm in value_count_dic:
        if elm in store2category:
            pos_dic[store2category[elm]] = value_count_dic[elm]

    print('pos_dic',pos_dic)

    pos_sign ={'기타':0,'카페':0,'분식':0,'술집':0,'숯불구이':0,'양식':0,'일식':0,'중식':0,'한식':0}
    for elm in pos_dic:
        if elm in pos_sign:
            pos_sign[elm] = pos_dic[elm]

    print('pos_sign',pos_sign)


    # fix 0607 0220
    grouped_users = users_df.groupby(['nickname','category']).count().reset_index()
    grouped_new_users = new_users_df.groupby(['nickname','category']).count().reset_index()

    for i in range(len(grouped_new_users)):
        if grouped_new_users['category'][i] in pos_sign:
            grouped_new_users['store'][i] = grouped_new_users['store'][i] + pos_sign[grouped_new_users['category'][i]]


    concated_df = pd.concat([grouped_users,grouped_new_users],ignore_index=True)


    pv_table = bm.make_pivot_table(concated_df)
    cs_table = bm.calculate_cosine_similarity(pv_table)

    similar_user = cf_r.search_simular_user(cs_table,new_user,args['select_top_n_user'])


    sort_table = cf_r.calculate_food_type(pv_table,new_user,similar_user)

    results= cf_r.cf_recommend(sort_table,store_tb,args['select_n_sotre'])
    results

    
    if len(results) ==0 :
        JSONResponse(status_code=400, content=dict(msg="NO_RESULT"))
    
    # final =[]
    # for result in results:
    #     final.append(db.query(Stores).filter(Stores.store == result).first())
    
    final = [] 
    for i in results:
        final_tmp = {}
        final_tmp['id'] = db.query(Stores).filter(Stores.store== i).first().id
        final_tmp['store'] = db.query(Stores).filter(Stores.store== i).first().store
        final_tmp['address'] = db.query(Stores).filter(Stores.store== i).first().address
        final_tmp['category'] = db.query(Stores).filter(Stores.store== i).first().category
        
        tmp = db.query(Users_like).filter(Users_like.nickname==user_nickname, Users_like.store==i).all()
        if len(tmp) == 0:
            user_like_store_whetherornot = 2 
        else:
            user_like_store_whetherornot = db.query(Users_like).filter(Users_like.nickname==user_nickname, Users_like.store==i).order_by(Users_like.updated_at.desc()).first().whetherornot
        final_tmp['userscrap'] = user_like_store_whetherornot
        
        final.append(final_tmp)

    return final




