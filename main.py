from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
import uvicorn
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

# 1. Path Parameter
@app.get("/users/{user_id}")
def get_user(user_id):
    return {"user_id":user_id}


# 2. Query Parameter
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/items/")
def read_item(skip: int = 0, limit: int = 10): # skip과 limit 변수 이용
    return fake_items_db[skip: skip + limit]


# 3. Optional Parameter
@app.get("/items/{item_id}")
def read_item(item_id: str, q: Optional[str] = None):  # Optional임을 명시하는 게 좋다.
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}



# 4. Request Body
# 1)Pydantic으로 Request Body 데이터 정의
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

# 2)Type inting으로 위에서 생성한 Item Class 주입
# 3)Request Body 데이터를 Validation
@app.post("/items/")
def create_item(item: Item):
    return item

# 5. Response Body
# Request Body로 들어갈 부분
class ItemIn(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

# Response Body로 들어갈 부분
class ItemOut(BaseModel):
    name: str
    price: float
    tax: Optional[float] = None

@app.post("/items/", response_model=ItemOut)
def create_item(item: ItemIn):
    return item


# 6. Form
templates = Jinja2Templates(directory='./')

@app.get("/login/") # Request 객체로 Request를 받는다.
def get_login_form(request: Request):	# login_form.html 파일이 필요하다
    return templates.TemplateResponse('login_form.html', context={'request': request})

@app.post("/login/")
def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)