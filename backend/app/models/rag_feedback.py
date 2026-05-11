from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base

class RAGFeedback(Base):
    __tablename__ = "rag_feedback"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question = Column(Text)
    answer = Column(Text)
    rating = Column(Integer)  # 1 = thumbs up, -1 = thumbs down
    created_at = Column(DateTime, default=datetime.utcnow)
