from datetime import datetime, timedelta

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
    Enum, Boolean,
)
from sqlalchemy.orm import Session

from app.database.conn import Base


class BaseMixin:
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False, default=func.utc_timestamp()) # create 된 시간 기록 # 근데 이 시간이 한국 시간이랑 안 맞음 -> (별로 중요한 건 아니지만) 수정해야 함
    updated_at = Column(DateTime, nullable=False, default=func.utc_timestamp(), onupdate=func.utc_timestamp()) # update 된 시간 기록 

    def all_columns(self):
        return [c for c in self.__table__.columns if c.primary_key is False and c.name != "created_at"] # 각 컬럼이 몇 개든 상관없음

    def __hash__(self):
        return hash(self.id)

    def create(self, session: Session, auto_commit=False, **kwargs):
        """
        테이블 데이터 적재 전용 함수
        :param session:
        :param auto_commit: 자동 커밋 여부
        :param kwargs: 적재 할 데이터
        :return:
        """
        for col in self.all_columns():
            col_name = col.name
            if col_name in kwargs:
                setattr(self, col_name, kwargs.get(col_name))
        session.add(self)
        session.flush()
        if auto_commit:
            session.commit()
        return self


class Users(Base, BaseMixin): # 이 부분과 우리 DB 컬럼을 변경해야 함   
    __tablename__ = "users"
    status = Column(Enum("active", "deleted", "blocked"), default="active")
    email = Column(String(length=255), nullable=True)
    pw = Column(String(length=2000), nullable=True)
    name = Column(String(length=255), nullable=True)
    phone_number = Column(String(length=20), nullable=True, unique=True)
    profile_img = Column(String(length=1000), nullable=True)
    sns_type = Column(Enum("FB", "G", "K"), nullable=True)
    marketing_agree = Column(Boolean, nullable=True, default=True)