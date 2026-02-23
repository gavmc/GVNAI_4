from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from db import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    message = Column(JSONB)

    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), index=True)
    session = relationship("Session", back_populates="messages")
    