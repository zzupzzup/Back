import pandas as pd 
import numpy as np

from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.conn import db
from app.database.schema import Users_prefer


def input_data(store_category, user_category):    
    selected_foods = []
        
    input_foods = user_category
    # if input_foods == '':
    #     break

    input_foods_list = input_foods.split()

    # 입력받은 값 중에서 foods 리스트에 있는 값만 선택하여 중복을 제거하고 리스트에 저장
    input_foods_list = list(set(input_foods_list).intersection(store_category))

    # 입력받은 값이 3개 이하인 경우에만 리스트에 추가
    if len(input_foods_list) <= 3:
        selected_foods.extend(input_foods_list)

    # 중복을 제거하여 최종 선택된 음식 종류 출력
    selected_foods = list(set(selected_foods))
    return selected_foods


def get_not_selected(selected_category, category):
    # 중복되는 값만 선택하여 리스트에 저장
    duplicate_values = list(set(selected_category).intersection(category))

    # 중복되는 값들을 제거하여 새로운 리스트에 저장
    not_selected = [value for value in category if value not in duplicate_values]

    return not_selected