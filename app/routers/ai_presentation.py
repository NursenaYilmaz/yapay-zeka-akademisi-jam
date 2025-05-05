
# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import mood as mood_model, user as user_model, ai_analysis
from app.routers.auth import get_current_user, teacher_owns_class
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
from collections import Counter
from app.services.gemini_service import GeminiService

# GeminiService'i import et - eğer hala kırmızı çizili görünüyorsa deneyin:
try:
    from app.services.gemini_service import GeminiService
except ImportError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from services.gemini_service import GeminiService

router = APIRouter()

class PresentationRequest(BaseModel):
    class_id: int
    subject: str
    topic: str
    template_type: Optional[str] = "balanced"  # balanced, interactive, visual

class PresentationAnalysis(BaseModel):
    analysis_id: int
    status: str
    presentation_content: Optional[Dict[str, Any]] = None

def analyze_presentation_background(
    analysis_id: int,
    class_id: int,
    subject: str,
    topic: str,
    template_type: str,
    db: Session
):
    """Arka planda Gemini ile analiz yap"""
    try:
        # Sınıfın mood verilerini al
        mood_entries = db.query(mood_model.MoodEntry).filter(
            mood_model.MoodEntry.class_id == class_id
        ).all()
        
        # Mood verilerini formatla
        mood_data = []
        for entry in mood_entries:
            mood_data.append({
                "user_id": entry.user_id,
                "mood": entry.mood,
                "score": entry.score,
                "timestamp": entry.timestamp.isoformat()
            })
        
        # Temel istatistikleri hesapla
        if mood_data:
            scores = [d["score"] for d in mood_data]
            moods = [d["mood"] for d in mood_data]
            average_score = sum(scores) / len(scores) if scores else 0
            mood_counts = dict(Counter(moods))
            dominant_mood = max(mood_counts, key=mood_counts.get) if mood_counts else "Normal"
        else:
            average_score = 15  # Default ortanca değer
            dominant_mood = "Normal"
        
        # Gemini ile analiz
        gemini_service = GeminiService()
        mood_analysis = gemini_service.analyze_mood_data(mood_data)
        
        # Sunum içeriği oluştur
        presentation_content = gemini_service.generate_presentation_content(
            mood_analysis=mood_analysis,
            subject=subject,
            topic=topic,
            template_type=template_type
        )
        
        # Veritabanına kaydet
        analysis = db.query(ai_analysis.AIAnalysis).filter(
            ai_analysis.AIAnalysis.id == analysis_id
        ).first()
        
        if analysis:
            analysis.mood_analysis = json.dumps(mood_analysis, ensure_ascii=False)
            analysis.presentation_content = json.dumps(presentation_content, ensure_ascii=False)
            analysis.average_mood_score = average_score
            analysis.dominant_mood = dominant_mood
            analysis.presentation_status = "completed"
            db.commit()
    
    except Exception as e:
        # Hata durumunda
        analysis = db.query(ai_analysis.AIAnalysis).filter(
            ai_analysis.AIAnalysis.id == analysis_id
        ).first()
        if analysis:
            analysis.presentation_status = "failed"
            analysis.presentation_content = json.dumps({"error": str(e)})
            db.commit()

@router.post("/generate", response_model=PresentationAnalysis)
async def generate_presentation(
    request: PresentationRequest,
    background_tasks: BackgroundTasks,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """AI ile sunum oluşturma işlemini başlat"""
    # Öğretmen kontrolü
    if current_user.teacher_id is not None:
        raise HTTPException(status_code=403, detail="Sadece öğretmenler sunum oluşturabilir.")
    
    # Sınıf kontrolü
    teacher_owns_class(current_user.id, request.class_id, db)
    
    # Analiz kaydı oluştur
    analysis = ai_analysis.AIAnalysis(
        teacher_id=current_user.id,
        class_id=request.class_id,
        subject=request.subject,
        topic=request.topic,
        presentation_status="pending"
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    # Arka planda analiz yap
    background_tasks.add_task(
        analyze_presentation_background,
        analysis.id,
        request.class_id,
        request.subject,
        request.topic,
        request.template_type,
        db
    )
    
    return PresentationAnalysis(
        analysis_id=analysis.id,
        status="pending"
    )

@router.get("/status/{analysis_id}", response_model=PresentationAnalysis)
def get_presentation_status(
    analysis_id: int,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sunum analiz durumunu getir"""
    analysis = db.query(ai_analysis.AIAnalysis).filter(
        ai_analysis.AIAnalysis.id == analysis_id,
        ai_analysis.AIAnalysis.teacher_id == current_user.id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analiz bulunamadı")
    
    presentation_content = None
    if analysis.presentation_content and analysis.presentation_status == "completed":
        try:
            presentation_content = json.loads(analysis.presentation_content)
        except:
            pass
    
    return PresentationAnalysis(
        analysis_id=analysis.id,
        status=analysis.presentation_status,
        presentation_content=presentation_content
    )

@router.get("/download/{analysis_id}")
def download_presentation(
    analysis_id: int,
    format: str = "markdown",  # markdown, pptx, pdf
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sunumu indir"""
    analysis = db.query(ai_analysis.AIAnalysis).filter(
        ai_analysis.AIAnalysis.id == analysis_id,
        ai_analysis.AIAnalysis.teacher_id == current_user.id
    ).first()
    
    if not analysis or analysis.presentation_status != "completed":
        raise HTTPException(status_code=404, detail="Sunum bulunamadı veya henüz hazır değil")
    
    presentation_content = json.loads(analysis.presentation_content)
    
    # Gemini servisini kullanarak formata dönüştür
    gemini_service = GeminiService()
    
    if format == "markdown":
        content = gemini_service.generate_presentation_slides(presentation_content, "markdown")
        return {
            "content": content,
            "filename": f"presentation_{analysis_id}.md"
        }
    elif format == "pptx":
        # Gelecekte PowerPoint oluşturma özelliği eklenebilir
        raise HTTPException(status_code=501, detail="PowerPoint formatı henüz desteklenmiyor")
    else:
        raise HTTPException(status_code=400, detail="Desteklenmeyen format")

@router.get("/teacher/analyses")
def get_teacher_analyses(
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Öğretmenin tüm analizlerini getir"""
    if current_user.teacher_id is not None:
        raise HTTPException(status_code=403, detail="Sadece öğretmenler erişebilir.")
    
    analyses = db.query(ai_analysis.AIAnalysis).filter(
        ai_analysis.AIAnalysis.teacher_id == current_user.id
    ).order_by(ai_analysis.AIAnalysis.created_at.desc()).all()
    
    return [
        {
            "id": analysis.id,
            "class_id": analysis.class_id,
            "subject": analysis.subject,
            "topic": analysis.topic,
            "status": analysis.presentation_status,
            "dominant_mood": analysis.dominant_mood,
            "average_mood_score": analysis.average_mood_score,
            "created_at": analysis.created_at
        }
        for analysis in analyses
    ]