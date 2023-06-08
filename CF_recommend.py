
# def search_simular_user(df,new_users,top_k):
#     # for user in new_users:
#     #     df[user].sort_values(ascending=False)[:top_k][1:].to_frame().reset_index()

import pandas as pd
import numpy as np

def search_simular_user(cs_table,new_user,top_n):
    # for user in new_user:
    #   similar_user =cs_table[user].sort_values(ascending=False)[:top_n][1:].index.tolist()
    similar_user =cs_table[new_user].sort_values(ascending=False)[:top_n][1:].index.tolist()
    # return similar_user[0]
    return similar_user

def calculate_food_type(pv_table,new_user,similar_user):
    cal_for_pv_table = pv_table.reset_index()

    # 음식 유형 뽑기
    food_type = cal_for_pv_table.columns[1:].tolist()

    # 새로운 유저의 음식 유형 정보
    food_type_of_new_user = cal_for_pv_table[cal_for_pv_table['nickname']== new_user].transpose().reset_index().iloc[1:,1]
    # 기존 유저의 음식 유형 정보
    # food_type_of_db_user = cal_for_pv_table[cal_for_pv_table['nickname']=='Jinny'].transpose().reset_index().iloc[1:,1]
    
    # 일단 이것은 가장 비슷한 한명의 유저와 비교함
    food_type_of_db_user = cal_for_pv_table[cal_for_pv_table['nickname']==similar_user[0]].transpose().reset_index().iloc[1:,1]


    # 새로운 유저와 기존 유저간의 음식 유형 정보 계산
    calculated_food_type = abs(food_type_of_new_user.subtract(food_type_of_db_user))


    calculated_type_count = pd.DataFrame({'category':food_type,'count':calculated_food_type})
    sort_temp = calculated_type_count.sort_values('count')

    # '''
    # 새로운 유저에게 추천해줄 음식 유형에 대한 정보가 정렬되어있으면
    # 정렬된 순서대로, 해당 유형에 해당하는 식당을 식당정보가(store_tb) 있는 테이블에서, 음식 유형(업태명)을 검색해서 

    # strategy 1.
    # 추천(일단 랜덤하게 5개)

    # strategy 2.
    # 추후 음식 유형별 n개씩, 해당 유형에 해당하는 식당 m개를 추천하는 형식으로도 확장 가능
    # '''

    sort_temp.reset_index(inplace=True,drop=True)
    
    return sort_temp

def cf_recommend(sort_table,store_tb,select_n):
    
    ranked_type_list = []

    recommend_list = []
    for i in range(len(sort_table)): # or top_n 개를 주어 몇개의 유형을 뽑을 건지 결정
      if sort_table.loc[i,'count']!=0:
        ranked_type_list.append(sort_table.loc[i,'category'])


# ranked_type_list

    for idx in range(len(ranked_type_list)):
      # print(ranked_type_list[idx])
      recommend  = store_tb[store_tb['category']==ranked_type_list[idx]].sort_values(['point','view'],ascending=False)['store'][:select_n].values.tolist()
      if select_n!=2:
        select_n-=1
      recommend_list.append(recommend)

    
    # recommend_list
    result = [item for sublist in recommend_list for item in sublist]

    return result

