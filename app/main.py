from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routers import ai

app = FastAPI()

# Statik dosyaları ve şablonları yükle
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Router'ları ekle
app.include_router(ai.router, prefix="/ai", tags=["ai"])

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/mood")
async def mood(request: Request):
    return templates.TemplateResponse("mood.html", {"request": request})

@app.get("/presentation")
async def presentation(request: Request):
    return templates.TemplateResponse("presentation.html", {"request": request})
