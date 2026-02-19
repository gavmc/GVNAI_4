from  sqlalchemy import Column, UUID
from sqlalchemy.orm import relationship
from src.db import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)

    messages = relationship("Message", back_populates="session")
