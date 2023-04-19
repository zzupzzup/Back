from enum import Enum

from pydantic.main import BaseModel
from pydantic.networks import EmailStr


class UserRegister(BaseModel): # json 으로 들어오고 json 으로 나가는 데이터들을 basemodel 을 이용해서 객체화   
    # pip install 'pydantic[email]'
    email: EmailStr = None
    pw: str = None


class SnsType(str, Enum): # Enum 외에 다른 값이 들어오면 422 ERROR 
    email: str = "email"
    facebook: str = "facebook"
    google: str = "google"
    kakao: str = "kakao"


class Token(BaseModel): # 이런 방식으로 토큰을 전달
    Authorization: str = None

class UserToken(BaseModel):
    id: int
    pw: str = None
    email: str = None
    name: str = None
    phone_number: str = None
    profile_img: str = None
    sns_type: str = None

    class Config:
        orm_mode = True