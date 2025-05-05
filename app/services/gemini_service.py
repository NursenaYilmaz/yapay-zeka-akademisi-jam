import os
import json
import google.generativeai as genai
from typing import Dict, Any, List
from pathlib import Path

class GeminiService:
    def __init__(self):
        """Gemini API'yi başlat"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY çevre değişkeni bulunamadı")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def analyze_mood_data(self, mood_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Mood verilerini analiz et"""
        prompt = f"""
        Aşağıdaki öğrenci ruh hali verilerini analiz et:
        {json.dumps(mood_data, ensure_ascii=False)}
        
        Şunları çıkar:
        1. Genel sınıf atmosferi
        2. Öne çıkan ruh hali eğilimleri
        3. Dikkat çekici noktalar
        4. Öğretim stratejisi önerileri
        
        Yanıtı JSON formatında ver:
        {{
            "general_atmosphere": "string",
            "mood_trends": ["string"],
            "notable_points": ["string"],
            "teaching_recommendations": ["string"]
        }}
        """
        
        response = self.model.generate_content(prompt)
        try:
            return json.loads(response.text)
        except:
            # Eğer JSON parse edilemezse, düz metin olarak döndür
            return {"raw_analysis": response.text}
    
    def generate_presentation_content(
        self, 
        mood_analysis: Dict[str, Any],
        subject: str,
        topic: str,
        template_type: str = "balanced"
    ) -> Dict[str, Any]:
        """Gemini kullanarak sunum içeriği oluştur"""
        
        template_structures = {
            "balanced": {
                "sections": ["Giriş", "Konu İncelemesi", "Öğrenci Katılımı", "Pratik Uygulamalar", "Sonuç"],
                "style": "Dengeli ve etkileşimli"
            },
            "interactive": {
                "sections": ["Soru ile Başlangıç", "Kavram Haritası", "Grup Etkinlikleri", "Tartışma", "Özet"],
                "style": "Aktif katılım odaklı"
            },
            "visual": {
                "sections": ["Görsel Giriş", "İnfografik", "Video Entegrasyonu", "Görsel Özetler", "Kapanış"],
                "style": "Görsel ağırlıklı"
            }
        }
        
        template = template_structures.get(template_type, template_structures["balanced"])
        
        prompt = f"""
        Aşağıdaki bilgileri kullanarak bir {subject} dersi sunumu hazırla:
        
        Konu: {topic}
        Sınıf Atmosferi: {mood_analysis.get('general_atmosphere', 'normal')}
        Öğretim Önerileri: {mood_analysis.get('teaching_recommendations', [])}
        
        Sunum Yapısı: {template['sections']}
        Sunum Stili: {template['style']}
        
        Her bölüm için:
        1. Başlık
        2. İçerik önerileri
        3. Aktivite/etkileşim fikirleri
        4. Görsel öneriler
        
        JSON formatında döndür:
        {{
            "title": "string",
            "sections": [
                {{
                    "title": "string",
                    "content": "string",
                    "activities": ["string"],
                    "visual_suggestions": ["string"]
                }}
            ]
        }}
        """
        
        response = self.model.generate_content(prompt)
        try:
            return json.loads(response.text)
        except:
            return {"raw_content": response.text}
    
    def generate_presentation_slides(
        self, 
        content: Dict[str, Any], 
        export_format: str = "pptx"
    ) -> str:
        """Sunumu slayt formatına dönüştür"""
        # Bu fonksiyon PowerPoint veya PDF oluşturabilir
        # Şimdilik markdown formatında döndürüyoruz
        
        markdown_content = f"# {content.get('title', 'Sunum')}\n\n"
        
        for section in content.get('sections', []):
            markdown_content += f"## {section.get('title', '')}\n\n"
            markdown_content += f"{section.get('content', '')}\n\n"
            
            if section.get('activities'):
                markdown_content += "### Aktiviteler:\n"
                for activity in section['activities']:
                    markdown_content += f"- {activity}\n"
                markdown_content += "\n"
            
            if section.get('visual_suggestions'):
                markdown_content += "### Görsel Öneriler:\n"
                for visual in section['visual_suggestions']:
                    markdown_content += f"- {visual}\n"
                markdown_content += "\n"
            
            markdown_content += "---\n\n"
        
        return markdown_content
