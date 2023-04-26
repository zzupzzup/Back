import json
from sentence_transformers import SentenceTransformer, CrossEncoder, util
import gzip
import os
from os import path
import torch
import pandas as pd

from rank_bm25 import BM25Okapi
from sklearn.feature_extraction import _stop_words
import string
from tqdm.autonotebook import tqdm
import numpy as np

import boto3
from connectS3 import upload_to_aws, download_from_aws


mps_device = torch.device("mps") # 나는 m1 맥북이라서 이렇게 했음.
    
bi_encoder = SentenceTransformer('jhgan/ko-sbert-multitask', device=mps_device)
bi_encoder.max_seq_length = 512     #Truncate long passages to 256 tokens
top_k = 32                          #Number of passages we want to retrieve with the bi-encoder

cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', device=mps_device)

if path.exists('mangoplate_review_raw.csv') == False:
    download_from_aws('mangoplate_review_raw.csv', 'zzup-s3-bucket', 'mangoplate_review_raw.csv')
mango_plate = pd.read_csv('mangoplate_review_raw.csv')
mango_clean = mango_plate.dropna(subset=['reviewtext'])
mango_clean = mango_clean.reset_index(drop=True)
passages = mango_clean['reviewtext']

# embedding_vec.npy 저장하기
#corpus_embeddings= bi_encoder.encode(passages, convert_to_tensor=True, show_progress_bar=True) # 매번 실행될 떄마다 1시간 걸림.
#corpus_embeddings_np = corpus_embeddings.cpu().numpy()
#np.save('embedding_vec.npy', corpus_embeddings_np)
#upload_to_aws('embedding_vec.npy', 'zzup-s3-bucket', 'embedding_vec.npy') # aws 에 업로드

if path.exists('embedding_vec.npy') == False:
    download_from_aws('embedding_vec.npy', 'zzup-s3-bucket', 'embedding_vec.npy') # aws 에서 다운로드

# embedding_vec.npy 불러오기
np_load = np.load('embedding_vec.npy')
corpus_embeddings = torch.from_numpy(np_load).to('mps')

def bm25_tokenizer(text):
    tokenized_doc = []
    for token in text.lower().split():
        token = token.strip(string.punctuation)

        if len(token) > 0 and token not in _stop_words.ENGLISH_STOP_WORDS:
            tokenized_doc.append(token)
    return tokenized_doc


tokenized_corpus = []
for passage in tqdm(passages):
    tokenized_corpus.append(bm25_tokenizer(passage))

bm25 = BM25Okapi(tokenized_corpus)


# This function will search all wikipedia articles for passages that
# answer the query
def search_test(query):
    print("Input question:", query)

    ##### BM25 search (lexical search) #####
    bm25_scores = bm25.get_scores(bm25_tokenizer(query))
    top_n = np.argpartition(bm25_scores, -5)[-5:]
    bm25_hits = [{'corpus_id': idx, 'score': bm25_scores[idx]} for idx in top_n]
    bm25_hits = sorted(bm25_hits, key=lambda x: x['score'], reverse=True)

    ##### Sematic Search #####
    # Encode the query using the bi-encoder and find potentially relevant passages
    question_embedding = bi_encoder.encode(query, convert_to_tensor=True)
    question_embedding = question_embedding.to(device=mps_device)
    hits = util.semantic_search(question_embedding, corpus_embeddings, top_k=top_k)
    hits = hits[0]  # Get the hits for the first query

    ##### Retrieval #####
    # Output of top-5 hits from bi-encoder
    topk_result = []
    print("\n————————————\n")
    print("Top-3 Bi-Encoder Retrieval hits")
    hits = sorted(hits, key=lambda x: x['score'], reverse=True)
    for hit in hits[0:3]:
        topk_result.append("\t{}".format(mango_clean['title'][hit['corpus_id']].replace("\n", " ")))
    return topk_result
