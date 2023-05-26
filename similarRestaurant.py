import pandas as pd
import numpy as np
import random

import sim_store as ss

from fastapi import APIRouter, Depends
from sqlalchemy import create_engine, text
from app.common.config import LocalConfig
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.conn import db
from app.database.schema import Stores, Users_prefer
from models import PersonalModel_Detail_Item

engine = create_engine(LocalConfig.DB_URL)
query_user = 'SELECT * FROM stores'
stores = pd.read_sql_query(sql=text(query_user), con=engine.connect())

from os import path
from connectS3 import upload_to_aws, download_from_aws

if path.exists('stores_sim.csv') == False:
        download_from_aws('stores_sim.csv', 'zzup-s3-bucket', 'stores_sim.csv')
sims = pd.read_csv('stores_sim.csv') 

#stores = pd.read_csv('./data/stores_U.csv') # stores table
#sims = pd.read_csv('./data/stores_sim.csv') # data 파일에 있음

# input_name = input("고객 클릭한 스토어의 이름:") # 고객이 클릭한 가게 이름을 넘겨주세요.

router = APIRouter() 

@router.get('/similarRestaurant', status_code= 201, response_model =list[PersonalModel_Detail_Item])
async def similarRestaurant(id : int ,user_id : int, db :Session = Depends(db.session)):
    
    store_name =  db.query(Stores).filter(Stores.id == id).first().store
    
    input_name = store_name
    
    input_id = ss.name_to_id(input_name, stores)

    result = ss.get_sim_store(sims, input_id)

    final = ss.id_to_name(result, stores)  # 결과 출력
    
    real_final = []
    for i in final :
        real_final.append(db.query(Stores).filter(Stores.store==i).first())

    return real_final