from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.db.database import Base

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    message_id = Column(String, unique=True, index=True)
    thread_id = Column(String, nullable=True)
    sender = Column(String, nullable=True)
    recipient = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    date = Column(String, nullable=True)
    body = Column(Text, nullable=True)
    raw = Column(Text)  # full structured JSON
