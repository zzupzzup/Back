from enum import Enum
from typing import List

from pydantic.main import BaseModel
from pydantic.networks import EmailStr


class Gender(str, Enum):
    woman : str = "woman"
    man : str = "man"
    
class Category(str, Enum):
    한식 : str = "한식"
    일식 : str = "일식"
    술집 : str = "술집"
    양식 : str = "양식"
    기타 : str = "기타"
    분식 : str = "분식"
    카페 : str = "카페"
    숯불구이 : str = "숯불구이"
    중식 : str = "중식"
    
class UserRegister_SignUp(BaseModel): # json 으로 들어오고 json 으로 나가는 데이터들을 basemodel 을 이용해서 객체화   
    # pip install 'pydantic[email]'
    email: EmailStr = None
    pw: str = None
    nickname : str = None
    age : int = None
    gender : Gender = None
    category : List[Category] = None
    
class UserRegister_SignIn(BaseModel):
    email: EmailStr = None
    pw: str = None

class SnsType(str, Enum): # Enum 외에 다른 값이 들어오면 422 ERROR 
    email: str = "email"
    #facebook: str = "facebook"
    #google: str = "google"
    #kakao: str = "kakao"


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
        
class PersonalModel_Item(BaseModel): # 개인화 추천 모델 일반페이지
    id : int = None
    store : str = None
    address : str = None
    category : str = None
    
    class Config:
        orm_mode = True
        
class PersonalModel_Detail_Item(BaseModel): # 개인화 추천 모델 상세페이지 
    id : int = None
    store : str = None
    img_url : str = None
    address : str = None
    category : str = None
    
    class Config:
        orm_mode = True
        
# 다음에 PersonalModel_Item 이랑 PersonalMdoel_Detail_Item 합쳐서 response_model_exclude 처리하자

class ChatRRS_Detail_Item(BaseModel): 
    #store : str = None
    #address : str = None
    reviewtext : str = None
    #score : float = None
    #category : str = None
    
    class Config:
        orm_mode = True
        
class Click_list(BaseModel):
    id : int = None
    store : str = None
    category : str = None
    address : str = None
    
    class Config:
        orm_mode = True
