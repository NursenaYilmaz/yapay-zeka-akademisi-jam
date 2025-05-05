from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float
from app.db.database import Base
from datetime import datetime

class AIAnalysis(Base):
    __tablename__ = "ai_analyses"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    class_id = Column(Integer)
    subject = Column(String)
    topic = Column(String)
    
    # Analiz sonuçları
    mood_analysis = Column(Text)  # JSON string
    presentation_content = Column(Text)  # Gemini'nin oluşturduğu içerik
    presentation_status = Column(String, default="pending")  # pending, completed, failed
    
    # Metrikler
    average_mood_score = Column(Float)
    dominant_mood = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PresentationTemplate(Base):
    __tablename__ = "presentation_templates"

    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String)
    template_content = Column(Text)  # Template yapısı (JSON veya markdown)
    created_at = Column(DateTime, default=datetime.utcnow)