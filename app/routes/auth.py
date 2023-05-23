from datetime import datetime, timedelta
import bcrypt
import jwt
from fastapi import APIRouter, Depends
# TODO:
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.common.consts import JWT_SECRET, JWT_ALGORITHM
from app.database.conn import db
from app.database.schema import Users, Users_prefer
from models import SnsType, Token, UserToken, UserRegister_SignIn, UserRegister_SignUp


router = APIRouter()
@router.post("/register", status_code=201 , response_model=Token)
async def register(sns_type: SnsType, reg_info: UserRegister_SignUp, session: Session = Depends(db.session)):
    """
    회원가입 API
    :param sns_type:
    :param reg_info:
    :param session:
    :return:
    """
    
    # sign up 관련 코드 # email sign up 
    # SnsType -> email 과 google 만 남기고 지우기 
    if sns_type == SnsType.email: 
        is_exist = await is_email_exist(reg_info.email)
        if not reg_info.email or not reg_info.pw :  
            return JSONResponse(status_code=400, content=dict(msg="Email and PW must be provided"))
        if is_exist: # 이미 기존에 존재하는 email 인 경우
            return JSONResponse(status_code=400, content=dict(msg="EMAIL_EXISTS"))
        hash_pw = bcrypt.hashpw(reg_info.pw.encode("utf-8"), bcrypt.gensalt()) # pw 해싱해서 저장할 목적 
        new_user = Users.create(session, auto_commit=True, pw=hash_pw, email=reg_info.email, nickname=reg_info.nickname, 
                                age=reg_info.age, gender=reg_info.gender) # email 과 pw 그리고 nickname, age, gender, category 를 DB 에 저장
        
        for category in reg_info.category:
            Users_prefer.create(session, auto_commit=True, nickname=reg_info.nickname, category=category)
        token = dict(Authorization=f"Bearer {create_access_token(data=UserToken.from_orm(new_user).dict(exclude={'pw', 'marketing_agree'}),)}")
        session.query(Users).filter(Users.email == new_user.email).update({'token' : token['Authorization']})
        session.commit()

        return token
    return JSONResponse(status_code=400, content=dict(msg="NOT_SUPPORTED"))


# login 관련 코드 # emain sign in 
@router.post("/login", status_code=200)
async def login(sns_type: SnsType, user_info: UserRegister_SignIn, db: Session = Depends(db.session)):
    if sns_type == SnsType.email:
        is_exist = await is_email_exist(user_info.email)
        if not user_info.email or not user_info.pw:
            return JSONResponse(status_code=400, content=dict(msg="Email and PW must be provided"))
        if not is_exist: 
            return JSONResponse(status_code=400, content=dict(msg="NO_MATCH_USER")) # DB 에 email 이 없을 때 NO_MATCH_USER 출력
        user = Users.get(email=user_info.email)
        is_verified = bcrypt.checkpw(user_info.pw.encode("utf-8"), user.pw.encode("utf-8"))
        if not is_verified:
            return JSONResponse(status_code=400, content=dict(msg="NO_MATCH_USER")) # pw 가 맞지 않을 때, NO_MATCH_USER 출력 
        token = dict(Authorization=f"Bearer {create_access_token(data=UserToken.from_orm(user).dict(exclude={'pw', 'marketing_agree'}),)}")
        search_db_users = db.query(Users).filter(Users.email == user_info.email).first()
        search_db_users_prefer = db.query(Users_prefer).filter(Users_prefer.nickname == search_db_users.nickname).all()
        
        # response_model 을 쓰고 싶은데 db 에서 나온 값이랑 모델에서 나온 값을 한 번에 처리하는 방법을 모르겠음
        result = token
        result['id'] = search_db_users.id
        result['email'] = search_db_users.email
        result['nickname'] = search_db_users.nickname
        result['age'] = search_db_users.age
        result['gender'] = search_db_users.gender
        
        tmp_category = []
        tmp_click = []
        cnt = 0
        for prefer in search_db_users_prefer :
            tmp_category.append(prefer.category)
            if prefer.store != None:
                tmp_click.append(prefer.store)
                cnt += 1
        result['category'] = ' '.join(tmp_category)
        result['click_log_cnt'] = cnt
        
        return result
    return JSONResponse(status_code=400, content=dict(msg="NOT_SUPPORTED"))


async def is_email_exist(email: str):
    get_email = Users.get(email=email) # get 는 schema.py 파일에 정의되어 있는데, DB 에 같은 메일이 2개 있으면 안되기 때문에 get 함수를 만들어서 사용
    if get_email:
        return True
    return False

def create_access_token(*, data: dict = None, expires_delta: int = None):
    to_encode = data.copy()
    if expires_delta:
        to_encode.update({"exp": datetime.utcnow() + timedelta(hours=expires_delta)})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt