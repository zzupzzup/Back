# import random

# def random_numbers(lst, n):
#     if n > len(lst):
#         return lst
#     else:
#         random.shuffle(lst)
#         return lst[:n]
    
# def get_sim_store(sims, store_id):
#     result = []
#     same_cat = []
#     sim = sims[str(store_id)]
#     for i in range(1142):
#         if i != store_id:
#             if sim[i] > 0.5:
#                 result.append(i)
#             elif sim[i] > 0 and sim[i] <=0.5:
#                 same_cat.append(i)


#     if len(result) < 10:
#         n = 10-len(result)
#         result += random_numbers(same_cat, n)
            
#     return result

# def name_to_id(input_name, stores):
#     for i in range(len(stores)):
#         if input_name == stores['store'][i]:
#             input_id = stores['id'][i]
    
#     return input_id

# def id_to_name(result_ids, stores):
#     result_names = []
#     for i in range(len(result_ids)):
#         for j in range(len(stores)):
#             if result_ids[i] == stores['id'][j]:
#                 result_names.append(stores['store'][j])
    
#     return result_names