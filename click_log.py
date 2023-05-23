from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.database.conn import db
from app.database.schema import Users, Users_for_personalModel, Users_prefer, Stores
from fastapi.responses import JSONResponse
from typing import Optional
from starlette.requests import Request
import requests

router = APIRouter()

@router.post('/click_log/{id}', status_code = 201)
async def click_log(id : int, user_id :int , db : Session = Depends(db.session)) :
    user_nickname = db.query(Users).filter(Users.id == user_id).first().nickname
    user_click_store = db.query(Stores).filter(Stores.id == id).first().store

    if user_nickname == None or user_click_store == None:
        JSONResponse(status_code=400, content=dict(msg="NO_RESULT"))

    Users_prefer.create(db, auto_commit=True, nickname=user_nickname, store=user_click_store)
    Users_for_personalModel.create(db, auto_commit=True, nickname=user_nickname, store=user_click_store)  
    return JSONResponse(status_code=201, content=dict(msg="SUCCESS"))