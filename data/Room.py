import datetime
from sqlalchemy import Column, String, Integer, DateTime
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class Room(SqlAlchemyBase, UserMixin):
    __tablename__ = 'Rooms'

    code = Column(String, nullable=True, primary_key=True)
    id_creator = Column(Integer, nullable=True, unique=False)
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))