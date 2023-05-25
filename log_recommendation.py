import pandas as pd 
import numpy as np

def get_df_log(input_log, stores):
    
    # 검색 결과를 담을 빈 데이터프레임 생성
    results = pd.DataFrame(columns=['store', 'point', 'view', 'review', 'star', 'address', 'category', 'join_key', 'menu', 'x', 'y'])

    # stores에서 가게 정보 검색해서 데이터 프레임 만들기
    for name in input_log:
        result = stores[stores['store'] == name.strip()]  # 가게 이름 앞뒤 공백 제거
        results = pd.concat([results, result])

    # 검색 결과 출력(고객이 클릭한 가게 정보 데이터 프레임)
    return results


def selected_remove(stores, first):
    for i in range(len(first)):
        condition = stores[stores['store'] == first[i]].index
        stores.drop(condition, inplace = True)
    return stores

def plus_log(remove_stores, log):
    results = []
    categories = log['category'].to_list()
    for i in range(len(categories)):
        # 조건 설정
        condition = remove_stores['category'] == categories[i]
        # 조건을 만족하는 행 랜덤하게 추출
        rows = remove_stores[condition].sample(n=2)


        # 추출된 행을 리스트로 변환
        result = rows['store'].values.tolist()
        results.append(result)
        
        # 위에서 선택된 가게 데이터 삭제
        remove_stores =  selected_remove(remove_stores, result)

    results = np.array(results).flatten().tolist()   
    return results
        
    
    
