from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.conn import db
from app.database.schema import Stores, Reviews, Users_like, Users
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post('/detail/{id}', status_code=201)
async def detail_page(user_id :int ,id : int, db : Session = Depends(db.session)) :
    store = db.query(Stores).filter(Stores.id == id ).first().store
    user_nickname = db.query(Users).filter(Users.id == user_id).first().nickname
    user_like_store = db.query(Stores).filter(Stores.id == id).first().store
    
    if store == None:
        JSONResponse(status_code=400, content=dict(msg="NO_RESULT"))
    
    store_review = db.query(Reviews).filter(Reviews.store == store).all()
    reviewtext = []
    for i in store_review:
        reviewtext.append(i.reviewtext)
    
    storeid = db.query(Stores).filter(Stores.store == store).first().id
    img_url = db.query(Stores).filter(Stores.store == store).first().img_url
    store_name = db.query(Stores).filter(Stores.store == store).first().store
    store_address = db.query(Stores).filter(Stores.store == store).first().address
    store_category = db.query(Stores).filter(Stores.store == store).first().category
    store_point = db.query(Stores).filter(Stores.store == store).first().point
    
    tmp = db.query(Users_like).filter(Users_like.nickname==user_nickname, Users_like.store==user_like_store).all()
    
    if len(tmp) == 0:
        user_like_store_whetherornot = 2
    else:
        user_like_store_whetherornot =  db.query(Users_like).filter(Users_like.nickname==user_nickname, Users_like.store==user_like_store).order_by(Users_like.updated_at.desc()).first().whetherornot
    
    final = {}
    final['id'] = storeid
    final['store'] = store_name
    final['point'] = store_point
    final['img_url'] = img_url
    final['address'] = store_address
    final['category'] = store_category
    final['reviewtext'] = reviewtext
    final['userscrap'] = user_like_store_whetherornot

    return final
    

