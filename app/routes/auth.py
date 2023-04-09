from datetime import datetime, timedelta
import bcrypt
import jwt
from fastapi import APIRouter, Depends
# TODO:
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.common.consts import JWT_SECRET, JWT_ALGORITHM
from app.database.conn import db
from app.database.schema import Users
from models import SnsType, Token, UserToken, UserRegister
"""
1. 구글 로그인을 위한 구글 앱 준비 (구글 개발자 도구)
2. FB 로그인을 위한 FB 앱 준비 (FB 개발자 도구)
3. 카카오 로그인을 위한 카카오 앱준비( 카카오 개발자 도구)
4. 이메일, 비밀번호로 가입 (v)
5. 가입된 이메일, 비밀번호로 로그인, (v)
6. JWT 발급 (v)
7. 이메일 인증 실패시 이메일 변경
8. 이메일 인증 메일 발송
9. 각 SNS 에서 Unlink 
10. 회원 탈퇴
11. 탈퇴 회원 정보 저장 기간 동안 보유(법적 최대 한도차 내에서, 가입 때 약관 동의 받아야 함, 재가입 방지 용도로 사용하면 가능)
"""
router = APIRouter()
@router.post("/register/{sns_type}", status_code=201 , response_model=Token)
async def register(sns_type: SnsType, reg_info: UserRegister, session: Session = Depends(db.session)):
    """
    회원가입 API
    :param sns_type:
    :param reg_info:
    :param session:
    :return:
    """
    
    # sign up 관련 코드 # email sign up
    # SnsType -> email 과 google 만 남기고 지우기 
    if sns_type == SnsType.email: # 진실이 -> 회원가입 창 만들라고 전달
        is_exist = await is_email_exist(reg_info.email)
        if not reg_info.email or reg_info.pw: # email 과 pw 가 공란인 경우 
            return JSONResponse(status_code=400, content=dict(msg="Email and PW must be provided'"))
        if is_exist: # 이미 기존에 존재하는 email 인 경우
            return JSONResponse(status_code=400, content=dict(msg="EMAIL_EXISTS"))
        hash_pw = bcrypt.hashpw(reg_info.pw.encode("utf-8"), bcrypt.gensalt()) # pw 해싱해서 저장할 목적 
        new_user = Users.create(session, auto_commit=True, pw=hash_pw, email=reg_info.email) # email 과 pw 를 DB 에 저장
        token = dict(Authorization=f"Bearer {create_access_token(data=UserToken.from_orm(new_user).dict(exclude={'pw', 'marketing_agree'}),)}")
        return token
    return JSONResponse(status_code=400, content=dict(msg="NOT_SUPPORTED"))


# login 관련 코드 # emain sign in 
@router.post("/login/{sns_type}", status_code=200)
async def login(sns_type: SnsType, user_info: UserRegister):
    if sns_type == SnsType.email:
        is_exist = await is_email_exist(user_info.email)
        if not user_info.email or not user_info.pw:
            return JSONResponse(status_code=400, content=dict(msg="Email and PW must be provided'"))
        if not is_exist: 
            return JSONResponse(status_code=400, content=dict(msg="NO_MATCH_USER")) # DB 에 email 이 없을 때 NO_MATCH_USER 출력
        user = Users.get(email=user_info.email)
        is_verified = bcrypt.checkpw(user_info.pw.encode("utf-8"), user.pw.encode("utf-8"))
        if not is_verified:
            return JSONResponse(status_code=400, content=dict(msg="NO_MATCH_USER")) # pw 가 맞지 않을 때, NO_MATCH_USER 출력 
        token = dict(Authorization=f"Bearer {create_access_token(data=UserToken.from_orm(user).dict(exclude={'pw', 'marketing_agree'}),)}")
        return token
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