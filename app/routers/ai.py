from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.ai_model import Presentation
import google.generativeai as genai
import os

router = APIRouter()

# Gemini API anahtarını ayarla
GOOGLE_API_KEY = "AIzaSyA79j_OVA1X9YfhrMNaZfPnJ3xVLESZHlw"
genai.configure(api_key=GOOGLE_API_KEY)

@router.post("/generate")
async def generate_presentation(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        
        # Gemini 1.5 Flash modelini başlat
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Sistem uyarısı ve gelişmiş prompt
        system_instruction = (
            "DİKKAT: Sana her zaman bir duygu teması verilecek. "
            "Cevabını mutlaka bu duygu temasına uygun şekilde yazmalısın. "
            "Duygu temasını göz ardı etme! "
            "Sunumun, verilen duyguya uygun bir dil ve üslupla yazılsın. "
            "Gereksiz maddeleme, uzun listeler veya tekrar eden ifadelerden kaçın. "
            "Sunumun her bölümü kısa, öz ve akıcı olsun. "
            "Her bölümde sadece en önemli noktaları vurgula. "
            "Her bölümde en fazla 3 cümle kullan. "
            "Sunumun tamamı 300 kelimeyi geçmesin. "
            "Sunumun sonunda özetleyici ve motive edici bir kapanış cümlesi ekle."
        )

        mood_text = {
            'happy': 'mutlu ve neşeli',
            'sad': 'üzgün ve duygusal',
            'energetic': 'enerjik ve dinamik',
            'tired': 'sakin ve rahatlatıcı'
        }.get(data.get('mood'), 'nötr')
        
        prompt = f"""{system_instruction}

Lütfen aşağıdaki konu için {mood_text} bir sunum hazırla:

Başlık: {data.get('title')}
İçerik: {data.get('content')}

Sunum şu formatta olmalı:
1. Giriş
2. Ana Bölümler
3. Sonuç

Her bölüm için kısa ve öz açıklamalar ekle.
"""
        
        # Gemini'den yanıt al
        response = model.generate_content(prompt)
        
        # Sunumu veritabanına kaydet
        presentation = Presentation(
            title=data.get('title'),
            content=response.text,
            template_type=data.get('mood')
        )
        
        db.add(presentation)
        db.commit()
        db.refresh(presentation)
        
        return {
            "message": "Sunum oluşturuldu",
            "presentation_id": presentation.id,
            "content": response.text
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 