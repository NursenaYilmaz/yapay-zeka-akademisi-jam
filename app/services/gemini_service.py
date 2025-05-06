import os
import json
import google.generativeai as genai
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    def __init__(self):
        """Gemini API'yi başlat"""
        # API key'i doğrudan tanımla
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        
        # Mevcut modelleri listele
        for m in genai.list_models():
            print(f"Model: {m.name}")
        
        # Model yapılandırması
        generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]
        
        # Model oluştur
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro-latest",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Sohbet geçmişi
        self.conversation_history: List[Dict] = []
        # Maksimum geçmiş sayısı
        self.max_history = 5
    
    def analyze_mood_data(self, mood_data: List[Dict]) -> Dict:
        """Sınıf ruh halini analiz et"""
        prompt = f"""
        Aşağıdaki sınıf ruh hali verilerini analiz et ve özetle:
        {json.dumps(mood_data, ensure_ascii=False)}
        
        Yanıtını şu formatta ver:
        {{
            "dominant_mood": "En yaygın ruh hali",
            "mood_distribution": {{"mood1": sayı, "mood2": sayı, ...}},
            "recommendations": ["öneri1", "öneri2", ...]
        }}
        """
        
        response = self.model.generate_content(prompt)
        return json.loads(response.text)
    
    def generate_presentation_content(
        self,
        mood_analysis: Dict,
        subject: str,
        topic: str,
        template_type: str = "balanced"
    ) -> Dict:
        """Sunum içeriği oluştur"""
        prompt = f"""
        Konu: {topic}
        Ders: {subject}
        Sınıf Ruh Hali Analizi: {json.dumps(mood_analysis, ensure_ascii=False)}
        Şablon Tipi: {template_type}
        
        Lütfen bu bilgilere göre bir sunum içeriği oluştur. İçerik şu bölümleri içermeli:
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
        
        response = self.model.generate_content(prompt)
        return json.loads(response.text)
    
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

    def ask_question(self, question: str) -> str:
        """Gemini'ye soru sor ve cevap al
        
        Args:
            question (str): Sorulacak soru
            
        Returns:
            str: Gemini'nin cevabı
        """
        try:
            response = self.model.generate_content(question)
            return response.text
        except Exception as e:
            return f"Soru cevaplanırken bir hata oluştu: {str(e)}"

    def _get_mood_prompt(self, mood: str) -> str:
        """Ruh haline göre prompt oluştur"""
        prompts = {
            "Yorgun": "Kullanıcı yorgun görünüyor. Daha kısa, öz ve motive edici yanıtlar ver. Kullanıcıyı yormadan, basit ve net açıklamalar yap.",
            "Dalgın": "Kullanıcı dalgın görünüyor. Daha dikkat çekici ve basit yanıtlar ver. Önemli noktaları vurgula ve tekrar et.",
            "Normal": "Kullanıcı normal bir ruh halinde. Dengeli ve standart yanıtlar ver. Detaylı açıklamalar yapabilirsin.",
            "Meraklı": "Kullanıcı meraklı görünüyor. Daha detaylı ve açıklayıcı yanıtlar ver. İlgi çekici örnekler ve ek bilgiler ekle.",
            "Enerjik": "Kullanıcı enerjik görünüyor. Daha dinamik ve etkileşimli yanıtlar ver. Aktif katılımı teşvik eden öneriler sun."
        }
        return prompts.get(mood, "Dengeli ve standart yanıtlar ver.")

    def _update_history(self, user_message: str, bot_response: str):
        """Sohbet geçmişini güncelle"""
        # Yeni mesajı ekle
        self.conversation_history.append({
            "user": user_message,
            "bot": bot_response,
            "timestamp": datetime.now()
        })
        
        # Geçmişi maksimum sayıda tut
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)

    def _get_conversation_context(self) -> str:
        """Sohbet geçmişini formatla"""
        if not self.conversation_history:
            return ""
        
        context = "Önceki konuşma geçmişi:\n"
        for entry in self.conversation_history:
            context += f"Kullanıcı: {entry['user']}\n"
            context += f"Bot: {entry['bot']}\n"
        return context

    async def send_message(self, message: str, mood: str = "Normal") -> str:
        """Kullanıcı mesajını işle ve yanıt döndür"""
        try:
            # Ruh haline göre prompt oluştur
            mood_prompt = self._get_mood_prompt(mood)
            
            # Sohbet geçmişini al
            conversation_context = self._get_conversation_context()
            
            # Tam prompt oluştur
            full_prompt = f"""
            {mood_prompt}
            
            {conversation_context}
            
            Kullanıcı: {message}
            """
            
            # Chat başlat
            chat = self.model.start_chat(history=[])
            
            # Mesajı gönder ve yanıtı al
            response = chat.send_message(full_prompt)
            
            # Yanıtı geçmişe ekle
            self._update_history(message, response.text)
            
            return response.text
        except Exception as e:
            print(f"Gemini API Hatası: {str(e)}")
            return "Üzgünüm, şu anda yanıt veremiyorum. Lütfen daha sonra tekrar deneyin."

    def convert_to_format(self, content: Dict, format: str) -> str:
        """İçeriği belirtilen formata dönüştür"""
        if format == "markdown":
            prompt = f"""
            Aşağıdaki sunum içeriğini Markdown formatına dönüştür:
            {json.dumps(content, ensure_ascii=False)}
            
            Markdown formatında yanıt ver.
            """
        elif format == "pptx":
            prompt = f"""
            Aşağıdaki sunum içeriğini PowerPoint sunumu için yapılandır:
            {json.dumps(content, ensure_ascii=False)}
            
            Her slayt için başlık ve içerik yapısını belirt.
            """
        else:
            raise ValueError(f"Desteklenmeyen format: {format}")
        
        response = self.model.generate_content(prompt)
        return response.text
