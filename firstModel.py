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

from fastapi import APIRouter, Depends
from sqlalchemy import create_engine, text
from app.common.config import LocalConfig
from os import path
from connectS3 import download_from_aws
from sqlalchemy.orm import Session
from app.database.conn import db
from app.database.schema import Stores
from models import PersonalModel_Item, PersonalModel_Detail_Item



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


@router.get('/firstModel', status_code=201, response_model=list[PersonalModel_Item]) # response_model 재활용
async def firstModel(user_category: str, db : Session = Depends(db.session)):
    result = []
    for i in firstRec(user_category) :
        result.append(db.query(Stores).filter(Stores.store == i).first())
    return result

@router.get('/firstModel/detail/{id}',  status_code=201, response_model=PersonalModel_Detail_Item) # response_model 재활용
async def firstModel_detail(id : int, db : Session = Depends(db.session)) :
    store = db.query(Stores).filter(Stores.id == id ).first().store
    return db.query(Stores).filter(Stores.store == store).first()