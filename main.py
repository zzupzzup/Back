from dataclasses import asdict
from typing import Optional
import uvicorn
from fastapi import FastAPI
from app.database.conn import db
from app.common.config import conf
from app.routes import index, auth
from fastapi.middleware.cors import CORSMiddleware

import torch
import chatRRS
from connectS3 import upload_to_aws, download_from_aws
from cloudpathlib import CloudPath


def create_app():
    """
    앱 함수 실행
    :return:
    """
    c = conf()
    app = FastAPI()
    conf_dict = asdict(c)
    db.init_app(app, **conf_dict)
    # 데이터 베이스 이니셜라이즈
    # 레디스 이니셜라이즈
    # 미들웨어 정의

    # 라우터 정의
    app.include_router(index.router)
    app.include_router(auth.router, tags=["Authentication"], prefix="/auth")
        
    #chatRRS -> 라우터 형태로 바꿔주기    
    @app.post('/chatRec')
    async def search_test(query: str):
        chatRec = chatRRS.search_test(query)
        return {'chatRec' : chatRec } 
    
    return app


app = create_app() 

# cors에러 해결 
origins = ["*"]

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)