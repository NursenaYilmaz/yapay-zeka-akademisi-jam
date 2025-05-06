import google.generativeai as genai
from typing import Dict, List
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Gemini API yapılandırması
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Model yapılandırması
model = genai.GenerativeModel('gemini-pro')

# Presentation templates
TEMPLATES = {
    "sade": "Sade ve minimalist bir sunum şablonu. Az metin, çok görsel.",
    "canlı": "Enerjik ve renkli bir sunum şablonu. İnteraktif elementler içerir.",
    "animasyonlu": "Animasyonlar ve geçişlerle zenginleştirilmiş sunum şablonu.",
    "minimal": "Çok az metin ve görsel içeren, öz sunum şablonu.",
    "hikaye": "Hikaye anlatımı formatında, akıcı bir sunum şablonu."
}

def get_template_for_mood(mood: str) -> str:
    """
    Ruh haline göre uygun şablonu seç
    """
    mood_templates = {
        "enerjik": "canlı",
        "normal": "sade",
        "yorgun": "minimal",
        "üzgün": "hikaye"
    }
    return mood_templates.get(mood, "sade")

def generate_lesson_content(
    topic: str,
    grade_level: str,
    mood: str,
    template: str = None
) -> Dict:
    """
    Gemini ile ders içeriği oluştur
    """
    if template is None:
        template = get_template_for_mood(mood)
    
    prompt = f"""
    Konu: {topic}
    Sınıf Seviyesi: {grade_level}
    Öğrenci Ruh Hali: {mood}
    Sunum Şablonu: {template}
    
    Lütfen bu bilgilere göre bir ders içeriği oluştur. İçerik şu bölümleri içermeli:
    1. Giriş
    2. Ana Konular
    3. Örnekler
    4. Alıştırmalar
    5. Özet
    
    Her bölüm için:
    - Başlık
    - İçerik
    - Görsel önerileri
    - Etkileşim önerileri
    
    Yanıtını JSON formatında ver. Örnek format:
    {{
        "giris": {{
            "baslik": "Giriş Başlığı",
            "icerik": "Giriş içeriği...",
            "gorsel_onerileri": ["görsel1", "görsel2"],
            "etkilesim_onerileri": ["öneri1", "öneri2"]
        }},
        "ana_konular": {{
            ...
        }},
        ...
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        content = response.text
        
        # JSON formatına dönüştür
        try:
            content_json = json.loads(content)
        except json.JSONDecodeError:
            # Eğer JSON formatında değilse, düz metni kullan
            content_json = {"raw_content": content}
        
        return {
            "content": content_json,
            "template": template,
            "mood": mood
        }
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")

def analyze_class_mood(mood_data: List[Dict]) -> Dict:
    """
    Sınıfın genel ruh halini analiz et ve öneriler sun
    """
    mood_counts = {}
    total_students = len(mood_data)
    
    for data in mood_data:
        mood = data["mood"]
        mood_counts[mood] = mood_counts.get(mood, 0) + 1
    
    # En yaygın ruh halini bul
    dominant_mood = max(mood_counts.items(), key=lambda x: x[1])[0]
    dominant_percentage = (mood_counts[dominant_mood] / total_students) * 100
    
    # Öneriler oluştur
    recommendations = {
        "enerjik": "Sınıf enerjik durumda. İnteraktif ve grup çalışmaları önerilir.",
        "normal": "Sınıf normal durumda. Standart ders akışı uygundur.",
        "yorgun": "Sınıf yorgun durumda. Kısa molalar ve görsel ağırlıklı içerik önerilir.",
        "üzgün": "Sınıfın moralini yükseltmek için eğlenceli aktiviteler ve hikaye anlatımı önerilir."
    }
    
    return {
        "dominant_mood": dominant_mood,
        "dominant_percentage": dominant_percentage,
        "mood_distribution": mood_counts,
        "recommendation": recommendations.get(dominant_mood, "Standart ders akışı uygundur.")
    } 