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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") 

app = FastAPI()

#실행하는 코드
# cd app
# uvicorn main:app --reload 

#cors에러 해결
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

@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}


# # 1. Path Parameter
# @app.get("/api/users/{user_id}") #api/users/{user_id} 라는 URL 요청이 발생하면 해당 함수를 실행해서 결과를 리턴하라는 의미
# def get_user(user_id):
#     return {"user_id":user_id}


# # 2. Query Parameter
# fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

# @app.get("/api/items/")
# def read_item(skip: int = 0, limit: int = 10): # skip과 limit 변수 이용
#     return fake_items_db[skip: skip + limit]


# # 3. Optional Parameter
# @app.get("/api/items/{item_id}")
# def read_item(item_id: str, q: Optional[str] = None):  # Optional임을 명시하는 게 좋다.
#     if q:
#         return {"item_id": item_id, "q": q}
#     return {"item_id": item_id}



# # 4. Request Body
# # 1)Pydantic으로 Request Body 데이터 정의
# class Item(BaseModel):
#     name: str
#     description: Optional[str] = None
#     price: float
#     tax: Optional[float] = None

# # 2)Type inting으로 위에서 생성한 Item Class 주입
# # 3)Request Body 데이터를 Validation
# @app.post("/api/items/")
# def create_item(item: Item):
#     return item

# # 5. Response Body
# # Request Body로 들어갈 부분
# class ItemIn(BaseModel):
#     name: str
#     description: Optional[str] = None
#     price: float
#     tax: Optional[float] = None

# # Response Body로 들어갈 부분
# class ItemOut(BaseModel):
#     name: str
#     price: float
#     tax: Optional[float] = None

# @app.post("/api/items/", response_model=ItemOut)
# def create_item(item: ItemIn):
#     return item

# # 6. Form
# templates = Jinja2Templates(directory='./')

# @app.get("/api/login/") # Request 객체로 Request를 받는다.
# def get_login_form(request: Request):	# login_form.html 파일이 필요하다
#     return templates.TemplateResponse('login_form.html', context={'request': request})

# @app.post("/api/login/")
# def login(username: str = Form(…), password: str = Form(…)):
#     return {"username": username}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)