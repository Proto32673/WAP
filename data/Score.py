from sqlalchemy import Column, Integer, ForeignKey
from .db_session import SqlAlchemyBase


class Score(SqlAlchemyBase):
    __tablename__ = 'score'

    id = Column(Integer, primary_key=True, autoincrement=True)
    max_score = Column(Integer, default=0)
    user_id = Column(Integer)