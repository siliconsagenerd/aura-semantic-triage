from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./aura_messages.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class MessageRecord(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    original_id = Column(Integer)
    text = Column(String, index=True)
    platform = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    urgency = Column(String)
    category = Column(String)
    sentiment = Column(String)
    emotion_score = Column(Float)
    suggested_reply = Column(String)
    ai_powered = Column(Boolean)
    feedback = Column(String, nullable=True)
    approved = Column(Boolean, nullable=True)
    feedback_timestamp = Column(DateTime, nullable=True)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
