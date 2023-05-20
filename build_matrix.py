import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

'''
user :  유저 정보테이블, [nickname,title]
store : 가게정보 테이블
'''

def merge_store_table(user,store):
    merged_df = pd.merge(user,store[['store', 'category']], on='store')

    return_df = merged_df
    return return_df

'''
입력 데이터프레임으론
유저, 가게이름,업태명,주된음식 이 있는 데이터프레임이 들어옴
'''



def make_pivot_table(df):
    grouped_df = df.groupby(['nickname', 'category']).count().reset_index()

    pivoted_df = pd.pivot_table(grouped_df,values='store',index='nickname',columns='category')

    pivoted_df = pivoted_df.fillna(0)
    return_df = pivoted_df.astype({'기타':'int','카페':'int','분식':'int','술집':'int','숯불구이':'int',
                                    '양식':'int','일식':'int','중식':'int','한식':'int'})
    
    return return_df

def calculate_cosine_similarity(matrix_dummy):
    user_similarity = cosine_similarity(matrix_dummy,matrix_dummy)
    user_similarity = pd.DataFrame(user_similarity,
                               index=matrix_dummy.index,
                               columns=matrix_dummy.index)
    
    return_df = user_similarity
    return return_df

# def search_simular_user(df,new_users,top_k):
#     # for user in new_users:
#     #     df[user].sort_values(ascending=False)[:top_k][1:].to_frame().reset_index()

def search_simular_user(cs_table,new_user,top_n):
    for user in new_user:
      similar_user =cs_table[user].sort_values(ascending=False)[:top_n][1:].index.tolist()

    return similar_user[0]  



