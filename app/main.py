from fastapi import FastAPI
from app.db.database import Base, engine
from fastapi.openapi.utils import get_openapi

# Model dosyaları (yalnızca veritabanı için kullanılır)
from app.models import user, mood as mood_model, presentation as presentation_model, ai_analysis

# Router dosyaları (FastAPI endpoint'leri için)
from app.routers import auth, mood as mood_router, presentation as presentation_router, chatbot, ai_presentation

app = FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Senin Projen",
        version="1.0.0",
        description="AI destekli eğitim platformu",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
# Veritabanı tablolarını oluştur
Base.metadata.create_all(bind=engine)

# Router'ları ekle
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(mood_router.router, prefix="/mood", tags=["Mood"])
app.include_router(presentation_router.router, prefix="/presentation", tags=["Presentation"])
app.include_router(chatbot.router, prefix="/chatbot", tags=["Chatbot"])
app.include_router(ai_presentation.router, prefix="/ai", tags=["AI Presentation"])

@app.get("/")
def read_root():
    return {"message": "BalanceED Backend is running 🎯"}
