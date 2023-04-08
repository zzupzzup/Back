from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import FastAPI, Form, Request, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Optional
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from dataclasses import asdict
from app.database.conn import db
from app.common.config import conf
from app.routes import index



def create_app():
    """
    앱 함수 실행
    :return:
    """
    c = conf() 
    app = FastAPI()
    conf_dict = asdict(c)
    db.init_app(app, **conf_dict) # fastAPI 와 DB 를 SQLAlchemy 를 이용해서 연결 
    # 데이터 베이스 이니셜라이즈

    # 레디스 이니셜라이즈

    # 미들웨어 정의

    # 라우터 정의
    app.include_router(index.router) # DB 에 값 추가 -> uvicorn main:app 실행 시키기 전에 /Back/app/routes/index.py index 함수에 추가할 값 넣기
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
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
    
#실행하는 코드 
# uvicorn main:app —reload  