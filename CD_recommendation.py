import pandas as pd 
import numpy as np
import itertools
import networkx as nx
import csv
from sklearn.preprocessing import MinMaxScaler

def min_max_nor(data):# 데이터셋을 2차원 배열로 변환
    # Min-Max 정규화 객체 생성
    scaler = MinMaxScaler(feature_range=(0.1, 0.9))
    data = [[x] for x in data]

    # Min-Max 정규화 수행
    scaler.fit(data)
    data_normalized = scaler.transform(data)

    # 정규화된 데이터 출력
    return data_normalized

def selected_foods_rec(selected_foods, stores):
    stores_list = []
    for i in range(len(selected_foods)):
        # 조건 설정
        condition = stores['category'] == selected_foods[i]

        # 조건을 만족하는 행 랜덤하게 추출
        rows = stores[condition].sample(n=5)

        # 추출된 행을 리스트로 변환
        result = rows['store'].values.tolist()
        stores_list.append(result)
        
    stores_list = np.array(stores_list).flatten().tolist()    
    return stores_list


def Cross_Domain_rec(stores, selected_foods, not_selected, G):
    weight_list = [0]*len(not_selected)
    for i in range(len(selected_foods)):
        for j in range(len(not_selected)):
            w = float(G[selected_foods[i]][not_selected[j]]['weight'])
            weight_list[j] += w
    
    df_weight = pd.DataFrame(weight_list, columns =['sum_weight'])
    df_type = pd.DataFrame(not_selected, columns = ['type'])
    df = pd.concat([df_type, df_weight], axis=1)
    df = df.sort_values('sum_weight', ascending=False)
    
    nor = min_max_nor(df['sum_weight'].to_list())
    df_nor = pd.DataFrame(nor, columns=['nor'])
    df = pd.concat([df, df_nor], axis=1)
    
    
    count = [nor[i]*5 for i in range(len(nor))]
    df_count = pd.DataFrame(count, columns=['count'])
    df_count = round(df_count)
    for i in range(len(df_count)):
        if df_count['count'][i] == 0:
            df_count['count'][i] = 1
    df = pd.concat([df, df_count], axis=1)
    
    
    stores_list = []
    for i in range(len(not_selected)):
        
        count = df[df['type']==not_selected[i]]
        count = count['count']
        # 조건 설정
        condition = stores['category'] == not_selected[i]

        # 조건을 만족하는 행 랜덤하게 추출
        rows = stores[condition].sample(n=int(count))
        
        # 추출된 행을 리스트로 변환
        result = rows['store'].values.tolist()
        stores_list.append(result)

        
    stores_list = list(itertools.chain(*stores_list))   
    return stores_list