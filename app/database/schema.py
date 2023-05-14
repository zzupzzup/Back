from datetime import datetime, timedelta
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
    Enum,
    Text
)
from sqlalchemy.dialects.mysql import FLOAT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import MetaData

from app.database.conn import Base, db


class BaseMixin:
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at = Column(DateTime, nullable=False, default=func.utc_timestamp(), onupdate=func.utc_timestamp())
    
    def __init__(self):
        self._q = None
        self._session = None


    def all_columns(self):
        return [c for c in self.__table__.columns if c.primary_key is False and c.name != "created_at"]

    def __hash__(self):
        return hash(self.id)

    @classmethod
    def create(cls, session: Session, auto_commit=False, **kwargs):
        """
        테이블 데이터 적재 전용 함수
        :param session:
        :param auto_commit: 자동 커밋 여부
        :param kwargs: 적재 할 데이터
        :return:
        """
        obj = cls()
        for col in obj.all_columns():
            col_name = col.name
            if col_name in kwargs:
                setattr(obj, col_name, kwargs.get(col_name))
        session.add(obj)
        session.flush()
        if auto_commit:
            session.commit()
        return obj

    @classmethod
    def get(cls, **kwargs):
        """
        Simply get a Row
        :param kwargs:
        :return:
        """
        session = next(db.session())
        query = session.query(cls)
        for key, val in kwargs.items():
            col = getattr(cls, key)
            query = query.filter(col == val)

        if query.count() > 1:
            raise Exception("Only one row is supposed to be returned, but got more than one.") 
        return query.first()
    
    @classmethod
    def filter(cls, session: Session = None, **kwargs):
        """
        Simply get a Row
        :param session:
        :param kwargs:
        :return:
        """
        cond = []
        for key, val in kwargs.items():
            key = key.split("__")
            if len(key) > 2:
                raise Exception("No 2 more dunders")
            col = getattr(cls, key[0])
            if len(key) == 1: cond.append((col == val))
            elif len(key) == 2 and key[1] == 'gt': cond.append((col > val))
            elif len(key) == 2 and key[1] == 'gte': cond.append((col >= val))
            elif len(key) == 2 and key[1] == 'lt': cond.append((col < val))
            elif len(key) == 2 and key[1] == 'lte': cond.append((col <= val))
            elif len(key) == 2 and key[1] == 'in': cond.append((col.in_(val)))

        obj = cls()
        if session:
            obj._session = session
            obj._sess_served = True
        else:
            obj._session = next(db.session())
            obj._sess_served = False
        query = obj._session.query(cls)
        query = query.filter(*cond)
        obj._q = query
        return obj


    @classmethod
    def cls_attr(cls, col_name=None):
        if col_name:
            col = getattr(cls, col_name)
            return col
        else:
            return cls

    def order_by(self, *args: str):
        for a in args:
            if a.startswith("-"):
                col_name = a[1:]
                is_asc = False
            else:
                col_name = a
                is_asc = True
            col = self.cls_attr(col_name)
            self._q = self._q.order_by(col.asc()) if is_asc else self._q.order_by(col.desc())
        return self


    def update(self, sess: Session = None, auto_commit: bool = False, **kwargs):
        cls = self.cls_attr()
        if sess:
            query = sess.query(cls)
        else:
            sess = next(db.session())
            query = sess.query(cls)
        self.close()
        return query.update(**kwargs)

    def first(self):
        result = self._q.first()
        self.close()
        return result

    def delete(self, auto_commit: bool = False, **kwargs):
        self._q.delete()
        if auto_commit:
            self._session.commit()
        self.close()

    def all(self):
        result = self._q.all()
        self.close()
        return result

    def count(self):
        result = self._q.count()
        self.close()
        return result

    def dict(self, *args: str):
        q_dict = {}
        for c in self.__table__.columns:
            if c.name in args:
                q_dict[c.name] = getattr(self, c.name)

        return q_dict

    def close(self):
        if self._sess_served:
            self._session.commit()
            self._session.close()
        else:
            self._session.flush()
            



class Users(Base, BaseMixin):
    __tablename__ = "users"
    status = Column(Enum("active", "deleted", "blocked"), default="active")
    email = Column(String(length=255), nullable=True)
    pw = Column(String(length=2000), nullable=True)
    nickname = Column(String(length=255), nullable=True)
    age = Column(Integer(), nullable=True)
    gender = Column(Enum("woman", "man"), nullable=True)
    store = Column(String(length=30), nullable=True)
    category = Column(Enum("한식","일식","술집","양식","기타","분식","까페","식육(숯불구이)","중식"))
    sns_type = Column(Enum("FB", "G", "K"), nullable=True)
    
class Stores(Base, BaseMixin):
    __tablename__ = "stores"
    store = Column(String(length=30), nullable=False)
    point = Column(FLOAT(), nullable=True)
    view = Column(Integer(), nullable=True)
    review = Column(Integer(), nullable=True)
    star = Column(Integer(), nullable=True)
    address = Column(String(length=255), nullable=True)
    category = Column(String(length=255), nullable=True)
    join_key = Column(String(length=255), nullable=True)
    menu = Column(String(length=255), nullable=True)

class Users_for_personalModel(Base, BaseMixin):
    __tablename__ = "users_for_personalModel"
    nickname = Column(String(length=255), nullable=False)
    store = Column(String(length=30), nullable=True)
    nickname = Column(String(length=255), nullable=True)
    
class Reviews(Base, BaseMixin):
    __tablename__ = "reviews"
    store = Column(String(length=30), nullable=False)
    nickname = Column(String(length=255), nullable=True)
    reviewtext = Column(Text(), nullable= True)
    review = Column(Text(), nullable=True)