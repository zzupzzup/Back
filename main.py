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

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "b493b60d13ada57d3d412dd71a3c5d104e06b67e727f44a621628a84e6d3c298"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/api/users/me/items")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]

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