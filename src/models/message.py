from sqlalchemy import Column, Integer
from sqlalchemy.dialects.postgresql import JSONB
from src.db import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    message = Column(JSONB)
    