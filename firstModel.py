import sys
import io
# sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
# sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')

# import warnings
# warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import networkx as nx
# import importlib
import csv

import select_type as st
import CD_recommendation as CD_r
import log_recommendation as lr

from fastapi import APIRouter, Depends
from sqlalchemy import create_engine, text
from app.common.config import LocalConfig
from os import path
from connectS3 import download_from_aws
from sqlalchemy.orm import Session
from app.database.conn import db
from app.database.schema import Stores, Users_prefer, Users, Users_like
from models import PersonalModel_Item, FirstModel_Item
from fastapi.responses import JSONResponse

router = APIRouter()


def firstRec(user_category: str): 
    # 가게 정보
    engine = create_engine(LocalConfig.DB_URL)
    query_user = 'SELECT * FROM stores'
    stores = pd.read_sql_query(sql=text(query_user), con=engine.connect())

    stores_category = stores['category'].unique().tolist()

    # weight_graph
    if path.exists('weighted_graph.csv') == False:
            download_from_aws('weighted_graph.csv', 'zzup-s3-bucket', 'weighted_graph.csv')
    with open('weighted_graph.csv') as file: # graph 는 데이터베이스 말고 s3 에 넣기
        reader = csv.DictReader(file)
        G = nx.Graph()
        for row in reader:
            G.add_edge(row['node1'], row['node2'], weight=row['weight'])
        
        
    selected_category = st.input_data(stores_category, user_category)
    not_selected_category = st.get_not_selected(selected_category, stores_category)

    selected_stores = CD_r.selected_foods_rec(selected_category, stores)
    CD_stores = CD_r.Cross_Domain_rec(stores, selected_category, not_selected_category, G)
    
    finals = []
    finals = selected_stores + CD_stores
    
    return finals

@router.get('/firstModel', status_code=201) # response_model 재활용, response_model=list[PersonalModel_Item]
async def firstModel(user_category: str, user_id : int, db : Session = Depends(db.session)):
    user_nickname = db.query(Users).filter(Users.id == user_id).first().nickname
    user_click_log = db.query(Users_prefer).filter(Users_prefer.nickname == user_nickname).all()
    
    engine = create_engine(LocalConfig.DB_URL)
    query_user = 'SELECT * FROM stores'
    stores = pd.read_sql_query(sql=text(query_user), con=engine.connect())
    
    user_clicked_stores = []
    for click in user_click_log :
        if click.store != None:
           user_clicked_stores.append(click.store)
    
    if len(user_clicked_stores) == 0:
        input_log = user_clicked_stores # 여기는 고객이 클릭한 가게이름 리스트를 넘겨주세요
    else:
        input_log = list(user_clicked_stores[-1:])
            
    if len(input_log) == 0:
        
        first = firstRec(user_category)
        Users_prefer.create(db, auto_commit=True, nickname=user_nickname, firstModelResult=str(first))      
    
        # final1 = []
        # for i in first:
        #     final1.append(db.query(Stores).filter(Stores.store == i).first())
        final1 = [] 
        for i in first:
            final1_tmp = {}
            final1_tmp['id'] = db.query(Stores).filter(Stores.store== i).first().id
            final1_tmp['store'] = db.query(Stores).filter(Stores.store== i).first().store
            final1_tmp['address'] = db.query(Stores).filter(Stores.store== i).first().address
            final1_tmp['category'] = db.query(Stores).filter(Stores.store== i).first().category
            
            tmp = db.query(Users_like).filter(Users_like.nickname==user_nickname, Users_like.store==i).all()
            if len(tmp) == 0:
                user_like_store_whetherornot = 2 
            else:
                user_like_store_whetherornot = db.query(Users_like).filter(Users_like.nickname==user_nickname, Users_like.store==i).order_by(Users_like.updated_at.desc()).first().whetherornot
            final1_tmp['userscrap'] = user_like_store_whetherornot
            
            final1.append(final1_tmp)
            
        return final1  # 로그 없을때 그냥 CD_recomandation 결과 출력
    
    else:  # 클릭한 식당의 카테고리와 같은 다른 식당 2개씩 더 추천(기존 추천된 항목 변하지 않고 추가만됨)
        
        #first_str = db.query(Users_prefer).filter(Users_prefer.nickname == user_nickname).first().firstModelResult
        #first_str = db.query(Users_prefer).filter(Users_prefer.nickname == user_nickname).order_by(Users_prefer.updated_at.desc()).first().firstModelResult
        first_str = db.query(Users_prefer).filter(Users_prefer.nickname == user_nickname).all()
        
        first_str_list = []
        for i in first_str:
            if i.firstModelResult != None: 
                first_str_list.append(i.firstModelResult)
        
        first_ = first_str_list[-1]
        first_ = eval(first_)
        
        df_log = lr.get_df_log(input_log, stores)

        remove_stores = lr.selected_remove(stores, first_) 
        log_stores = lr.plus_log(remove_stores, df_log)
        result = list(log_stores) + first_
        
        Users_prefer.create(db, auto_commit=True, nickname=user_nickname, firstModelResult=str(result))
        
        # final2 = []
        # for i in result:
        #     final2.append(db.query(Stores).filter(Stores.store == i).first())
            
        final2 = [] # 와 너무 비효율적인걸?
        for i in result:
            final2_tmp = {}
            final2_tmp['id'] = db.query(Stores).filter(Stores.store== i).first().id
            final2_tmp['store'] = db.query(Stores).filter(Stores.store== i).first().store
            final2_tmp['address'] = db.query(Stores).filter(Stores.store== i).first().address
            final2_tmp['category'] = db.query(Stores).filter(Stores.store== i).first().category
            
            tmp = db.query(Users_like).filter(Users_like.nickname==user_nickname, Users_like.store==i).all()
            if len(tmp) == 0:
                user_like_store_whetherornot = 2 
            else:
                user_like_store_whetherornot = db.query(Users_like).filter(Users_like.nickname==user_nickname, Users_like.store==i).order_by(Users_like.updated_at.desc()).first().whetherornot
            final2_tmp['userscrap'] = user_like_store_whetherornot
            
            final2.append(final2_tmp)
                    
        return final2
    
                
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    

    # user_click_list = []
    # for click in user_click_log:
    #     if click.store != None:
    #         user_click_list.append(click.store)
    
    
    # if log.empty:   # 로그 없을때 그냥 CD_recomandation 결과 출력
    #     return first
    # else:  # 클릭한 식당의 카테고리와 같은 다른 식당 2개씩 더 추천(기존 추천된 항목 변하지 않고 추가만됨)
    #     remove_stores = lr.selected_remove(user_click_list, first) 
    #     log_stores = lr.plus_log(remove_stores, log)
    #     result = log_stores+first
    #     return result

    # if len(first) == 0 and len(result) ==0 :
    #     JSONResponse(status_code=400, content=dict(msg="NO_RESULT"))
    # return JSONResponse(status_code=201, content=dict(msg="SUCCESS"))
    
    
    
    #return stores

# @router.get('/firstModel/detail/{id}',  status_code=201, response_model=PersonalModel_Detail_Item) # response_model 재활용
# async def firstModel_detail(id : int, db : Session = Depends(db.session)) :
#     store = db.query(Stores).filter(Stores.id == id ).first().store
#     return db.query(Stores).filter(Stores.store == store).first()