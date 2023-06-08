from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.database.conn import db
from app.database.schema import Users, Stores, Users_like
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post('/userLike/{id}', status_code = 201)
async def user_like(id : int, user_id :int , db : Session = Depends(db.session)) :
    user_nickname = db.query(Users).filter(Users.id == user_id).first().nickname
    user_like_store = db.query(Stores).filter(Stores.id == id).first().store
    
    if user_nickname == None or user_like_store == None:
        JSONResponse(status_code=400, content=dict(msg="NO_RESULT"))
    
    Users_like.create(db, auto_commit=True, nickname=user_nickname, store=user_like_store, whetherornot=1) # uers_like table 에 사용자가 좋아요 한 것 추가
    
    return JSONResponse(status_code=201, content=dict(msg="SUCCESS"))
    
@router.post('/userUnlike/{id}', status_code = 201)
async def user_unlike(id : int, user_id :int , db : Session = Depends(db.session)) :
    user_nickname = db.query(Users).filter(Users.id == user_id).first().nickname
    user_like_store = db.query(Stores).filter(Stores.id == id).first().store
    
    if user_nickname == None or user_like_store == None:
        JSONResponse(status_code=400, content=dict(msg="NO_RESULT"))
    
    Users_like.create(db, auto_commit=True, nickname=user_nickname, store=user_like_store, whetherornot=0) # uers_like table 에 사용자가 좋아요 한 것 추가
    
    return JSONResponse(status_code=201, content=dict(msg="SUCCESS"))

