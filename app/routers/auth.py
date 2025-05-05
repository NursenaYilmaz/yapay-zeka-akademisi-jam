# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.db.database import get_db
from app.models import user as user_model
import bcrypt
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os

router = APIRouter()

# OAuth2 şemasını doğru şekilde tanımlayın
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"  # Token endpoint'inizi buraya yazın
)

# .env'den JWT_SECRET_KEY'i al
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik doğrulanamadı",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def teacher_only(current_user: user_model.User = Depends(get_current_user)):
    if current_user.teacher_id is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sadece öğretmenler erişebilir.")
    return current_user

def student_only(current_user: user_model.User = Depends(get_current_user)):
    if current_user.teacher_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sadece öğrenciler erişebilir.")
    return current_user

def student_from_teacher(teacher_id: int, student_id: int, db: Session):
    """Öğrencinin, belirtilen öğretmene ait olup olmadığını kontrol eder"""
    student = db.query(user_model.User).filter(
        user_model.User.id == student_id,
        user_model.User.teacher_id == teacher_id
    ).first()
    
    if not student:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                          detail="Bu öğrenciye erişim yetkiniz yok.")
    return student

def same_class_check(user_id: int, class_id: int, db: Session):
    """Kullanıcının belirtilen sınıfa ait olup olmadığını kontrol eder"""
    user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    
    if not user or user.class_id != class_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                          detail="Bu sınıfa erişim yetkiniz yok.")
    return user

def teacher_owns_class(teacher_id: int, class_id: int, db: Session):
    """Öğretmenin belirtilen sınıfı yönetip yönetmediğini kontrol eder"""
    # Sınıfa ait öğrencileri kontrol et
    students = db.query(user_model.User).filter(
        user_model.User.class_id == class_id,
        user_model.User.teacher_id == teacher_id
    ).first()
    
    if not students:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                          detail="Bu sınıfı yönetme yetkiniz yok.")
    return True

class UserCreate(BaseModel):
    username: str
    password: str
    teacher_id: Optional[int] = None
    class_id: Optional[int] = None

@router.post("/register")
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(user_model.User).filter(user_model.User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten var.")

    hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())

    new_user = user_model.User(
        username=user_data.username,
        password=hashed_password.decode('utf-8'),
        teacher_id=user_data.teacher_id,
        class_id=user_data.class_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Kayıt başarılı!",
        "user_id": new_user.id
    }

class UserLogin(BaseModel):
    username: str
    password: str

@router.post("/login")
def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(user_model.User).filter(user_model.User.username == user_data.username).first()

    if not user or not bcrypt.checkpw(user_data.password.encode('utf-8'), user.password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Geçersiz kullanıcı adı veya şifre.")

    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "message": "Giriş başarılı!",
        "access_token": access_token,
        "user_id": user.id,
        "username": user.username,
        "is_teacher": user.teacher_id is None,
        "class_id": user.class_id
    }

@router.get("/teacher/{teacher_id}/students")
def get_students_by_teacher(
    teacher_id: int,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Sadece kendi öğrencilerini görebilsin
    if current_user.id != teacher_id:
        raise HTTPException(status_code=403, detail="Bu verilere erişim yetkiniz yok.")

    students = db.query(user_model.User).filter(user_model.User.teacher_id == teacher_id).all()

    return [
        {
            "user_id": student.id,
            "username": student.username,
            "class_id": student.class_id
        }
        for student in students
    ]

@router.get("/auth/user-info")
def get_user_info(current_user: user_model.User = Depends(get_current_user)):
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "teacher_id": current_user.teacher_id,
        "is_teacher": current_user.teacher_id is None,
        "class_id": current_user.class_id
    }

class PasswordUpdateRequest(BaseModel):
    new_password: str

@router.put("/user/{user_id}/update-password")
def update_user_password(
    user_id: int,
    password_data: PasswordUpdateRequest,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Sadece kendi şifresini değiştirebilsin
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Sadece kendi şifrenizi değiştirebilirsiniz.")
    
    user = db.query(user_model.User).filter(user_model.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")

    hashed_password = bcrypt.hashpw(password_data.new_password.encode('utf-8'), bcrypt.gensalt())
    user.password = hashed_password.decode('utf-8')

    db.commit()
    db.refresh(user)

    return {"message": "Şifre başarıyla güncellendi."}

@router.get("/class/{class_id}/students")
def get_students_by_class(
    class_id: int, 
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Öğretmen olup olmadığını kontrol et
    if current_user.teacher_id is not None:
        raise HTTPException(status_code=403, detail="Sadece öğretmenler erişebilir.")
    
    # Öğretmenin bu sınıfı yönetip yönetmediğini kontrol et
    teacher_owns_class(current_user.id, class_id, db)
    
    students = db.query(user_model.User).filter(user_model.User.class_id == class_id).all()

    if not students:
        raise HTTPException(status_code=404, detail="Bu sınıfa ait öğrenci bulunamadı.")

    return [
        {
            "user_id": student.id,
            "username": student.username
        }
        for student in students
    ]
