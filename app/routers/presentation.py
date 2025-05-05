from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import presentation as presentation_model
from app.models import user as user_model
from app.routers.auth import get_current_user, teacher_owns_class, same_class_check
from datetime import datetime
import os
from typing import List

router = APIRouter()

UPLOAD_DIR = "presentations"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_presentation(
    class_id: int = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user)
):
    # Sadece öğretmenler sunum yükleyebilir
    if current_user.teacher_id is not None:
        raise HTTPException(status_code=403, detail="Sadece öğretmenler sunum yükleyebilir.")
    
    # Öğretmenin bu sınıfı yönetip yönetmediğini kontrol et
    teacher_owns_class(current_user.id, class_id, db)
    
    file_location = f"{UPLOAD_DIR}/{class_id}_{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Veritabanına kayıt
    new_presentation = presentation_model.Presentation(
        class_id=class_id,
        title=title,
        file_path=file_location,
        upload_timestamp=datetime.utcnow()
    )
    db.add(new_presentation)
    db.commit()
    db.refresh(new_presentation)

    return {
        "message": "Sunum başarıyla yüklendi.",
        "file_path": file_location,
        "title": title,
        "class_id": class_id
    }

@router.get("/presentations/{class_id}")
def list_presentations(
    class_id: int,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Öğretmen mi yoksa öğrenci mi kontrolü
    if current_user.teacher_id is None:  # Öğretmen ise
        teacher_owns_class(current_user.id, class_id, db)
    else:  # Öğrenci ise
        same_class_check(current_user.id, class_id, db)
    
    files = [f for f in os.listdir(UPLOAD_DIR) if f.startswith(f"{class_id}_")]
    return {
        "class_id": class_id,
        "presentations": files
    }

@router.get("/class/{class_id}", response_model=List[dict])
def get_presentations_for_class(
    class_id: int, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user)
):
    # Öğretmen mi yoksa öğrenci mi kontrolü
    if current_user.teacher_id is None:  # Öğretmen ise
        teacher_owns_class(current_user.id, class_id, db)
    else:  # Öğrenci ise
        same_class_check(current_user.id, class_id, db)
    
    presentations = db.query(presentation_model.Presentation).filter(
        presentation_model.Presentation.class_id == class_id
    ).all()

    if not presentations:
        raise HTTPException(status_code=404, detail="Bu sınıf için sunum bulunamadı.")

    return [
        {
            "title": p.title,
            "file_path": p.file_path,
            "upload_timestamp": p.upload_timestamp
        }
        for p in presentations
    ]

from sqlalchemy import desc  # en son ekleneni bulmak için

@router.get("/latest/{class_id}")
def get_latest_presentation(
    class_id: int, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user)
):
    # Öğretmen mi yoksa öğrenci mi kontrolü
    if current_user.teacher_id is None:  # Öğretmen ise
        teacher_owns_class(current_user.id, class_id, db)
    else:  # Öğrenci ise
        same_class_check(current_user.id, class_id, db)
    
    latest_presentation = (
        db.query(presentation_model.Presentation)
        .filter(presentation_model.Presentation.class_id == class_id)
        .order_by(presentation_model.Presentation.upload_timestamp.desc())
        .first()
    )

    if not latest_presentation:
        return {"message": "Henüz bu sınıfa ait bir sunum yüklenmedi."}

    return {
        "class_id": latest_presentation.class_id,
        "filename": latest_presentation.file_path,
        "title": latest_presentation.title,
        "timestamp": latest_presentation.upload_timestamp.isoformat(),
    }

@router.get("/student/class/{class_id}/presentations")
def get_presentations_for_student(
    class_id: int, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user)
):
    # Sadece öğrenciler erişebilir
    if current_user.teacher_id is None:
        raise HTTPException(status_code=403, detail="Sadece öğrenciler erişebilir.")
    
    # Öğrencinin aynı sınıftan olup olmadığını kontrol et
    same_class_check(current_user.id, class_id, db)

    presentations = db.query(presentation_model.Presentation).filter(
        presentation_model.Presentation.class_id == class_id
    ).all()

    return [
        {
            "title": p.title,
            "download_link": f"/files/{p.file_path}",
            "uploaded_at": p.upload_timestamp
        } for p in presentations
    ]

@router.get("/student/{student_id}/presentation/{presentation_id}/detail")
def get_presentation_detail_for_student(
    student_id: int, 
    presentation_id: int, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user)
):
    # Sadece öğrenciler erişebilir
    if current_user.teacher_id is None:
        raise HTTPException(status_code=403, detail="Sadece öğrenciler erişebilir.")
    
    # Sadece kendi bilgisini görebilsin
    if current_user.id != student_id:
        raise HTTPException(status_code=403, detail="Sadece kendi bilginizi görebilirsiniz.")
    
    # Sunumu kontrol et: öğrenci ile aynı sınıfa ait mi
    presentation = db.query(presentation_model.Presentation).filter(
        presentation_model.Presentation.id == presentation_id,
        presentation_model.Presentation.class_id == current_user.class_id
    ).first()

    if not presentation:
        raise HTTPException(status_code=404, detail="Bu sunum bu öğrenciye ait sınıfla eşleşmiyor.")

    # Sunumu yükleyen öğretmeni al
    teacher = db.query(user_model.User).filter(user_model.User.id == presentation.teacher_id).first()
    teacher_name = teacher.username if teacher else "Bilinmiyor"

    return {
        "presentation_id": presentation.id,
        "title": presentation.title,
        "description": presentation.description,
        "uploaded_at": presentation.upload_timestamp,
        "teacher_name": teacher_name,
        "download_link": f"/files/{presentation.file_path}"
    }

@router.get("/student/{class_id}/presentations")
def get_presentations_for_student(
    class_id: int, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user)
):
    # Sadece öğrenciler erişebilir
    if current_user.teacher_id is None:
        raise HTTPException(status_code=403, detail="Sadece öğrenciler erişebilir.")
    
    # Öğrencinin aynı sınıftan olup olmadığını kontrol et
    same_class_check(current_user.id, class_id, db)

    presentations = db.query(presentation_model.Presentation).filter(
        presentation_model.Presentation.class_id == class_id
    ).all()

    return [
        {
            "title": p.title,
            "download_link": f"/files/{p.file_path}",
            "uploaded_at": p.upload_timestamp
        } for p in presentations
    ]

@router.get("/teacher/{teacher_id}/class/{class_id}/presentations")
def get_presentations_for_teacher_class(
    teacher_id: int, 
    class_id: int, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user)
):
    # Sadece öğretmenler erişebilir
    if current_user.teacher_id is not None:
        raise HTTPException(status_code=403, detail="Sadece öğretmenler erişebilir.")
    
    # Sadece kendi bilgisini görebilsin
    if current_user.id != teacher_id:
        raise HTTPException(status_code=403, detail="Sadece kendi sınıfınızı görebilirsiniz.")
    
    # Bu sınıfı yönetip yönetmediğini kontrol et
    teacher_owns_class(current_user.id, class_id, db)

    presentations = db.query(presentation_model.Presentation).filter(
        presentation_model.Presentation.class_id == class_id
    ).all()

    return [
        {
            "title": p.title,
            "file_path": p.file_path,
            "uploaded_at": p.upload_timestamp
        } for p in presentations
    ]
