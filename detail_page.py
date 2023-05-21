from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.conn import db
from app.database.schema import Stores, Reviews
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post('/detail/{id}', status_code=201)
async def detail_page(id : int, db : Session = Depends(db.session)) :
    store = db.query(Stores).filter(Stores.id == id ).first().store
    
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
    
    final = {}
    final['id'] = storeid
    final['store'] = store_name
    final['img_url'] = img_url
    final['address'] = store_address
    final['category'] = store_category
    final['reviewtext'] = reviewtext
    
    return final

