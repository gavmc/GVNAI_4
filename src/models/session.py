from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db import Base
from uuid import uuid4


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)

    messages = relationship("Message", back_populates="session")
