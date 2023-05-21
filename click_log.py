from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.database.conn import db
from app.database.schema import Users, Users_for_personalModel, Users_prefer, Stores

router = APIRouter()

@router.post('/click_log/{id}', status_code = 201)
async def click_log(id : int, token : str = Header(default=None) , db : Session = Depends(db.session)) :
    user_nickname = db.query(Users).filter(Users.token == token).first().nickname
    user_click_store = db.query(Stores).filter(Stores.id == id).first().store

    Users_prefer.create(db, auto_commit=True, nickname=user_nickname, store=user_click_store)
    Users_for_personalModel.create(db, auto_commit=True, nickname=user_nickname, store=user_click_store)
    return
    