# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.db.database import get_db
from app.models import user as user_model
import bcrypt
from fastapi.security import OAuth2PasswordBearer
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = db.query(user_model.User).filter(user_model.User.username == token).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz kullanıcı.")
    return user

def teacher_only(current_user: user_model.User = Depends(get_current_user)):
    if current_user.teacher_id is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sadece öğretmenler erişebilir.")
    return current_user

def student_only(current_user: user_model.User = Depends(get_current_user)):
    if current_user.teacher_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sadece öğrenciler erişebilir.")
    return current_user

class UserCreate(BaseModel):
    username: str
    password: str
    teacher_id: Optional[int] = None

@router.post("/register")
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(user_model.User).filter(user_model.User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten var.")

    hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())

    new_user = user_model.User(
        username=user_data.username,
        password=hashed_password.decode('utf-8'),
        teacher_id=user_data.teacher_id
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
def login_user(user_data: UserLogin, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    user = db.query(user_model.User).filter(user_model.User.username == user_data.username).first()

    if not user or not bcrypt.checkpw(user_data.password.encode('utf-8'), user.password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Geçersiz kullanıcı adı veya şifre.")

   
    access_token = Authorize.create_access_token(subject=str(user.id))

    return {
        "message": "Giriş başarılı!",
        "access_token": access_token,
        "user_id": user.id,
        "username": user.username,
        "is_teacher": user.teacher_id is None
    }

@router.get("/teacher/{teacher_id}/students")
def get_students_by_teacher(
    teacher_id: int,
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db)
):
    try:
        Authorize.jwt_required()
    except AuthJWTException as e:
        raise HTTPException(status_code=401, detail="Token geçersiz")

    current_user_id = int(Authorize.get_jwt_subject())
    current_user = db.query(user_model.User).filter(user_model.User.id == current_user_id).first()

    if not current_user or current_user.id != teacher_id:
        raise HTTPException(status_code=403, detail="Bu verilere erişim yetkiniz yok.")

    students = db.query(user_model.User).filter(user_model.User.teacher_id == teacher_id).all()

    return [
        {
            "user_id": student.id,
            "username": student.username
        }
        for student in students
    ]

@router.get("/auth/user-info")
def get_user_info(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    try:
        Authorize.jwt_required()
    except AuthJWTException as e:
        raise HTTPException(status_code=401, detail="Yetkisiz")

    current_user_id = Authorize.get_jwt_subject()
    user = db.query(user_model.User).filter(user_model.User.id == int(current_user_id)).first()

    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")

    return {
        "user_id": user.id,
        "username": user.username,
        "teacher_id": user.teacher_id,
        "is_teacher": user.teacher_id is None
    }

class PasswordUpdateRequest(BaseModel):
    new_password: str

@router.put("/user/{user_id}/update-password")
def update_user_password(
    user_id: int,
    password_data: PasswordUpdateRequest,
    db: Session = Depends(get_db)
):
    user = db.query(user_model.User).filter(user_model.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")

    hashed_password = bcrypt.hashpw(password_data.new_password.encode('utf-8'), bcrypt.gensalt())
    user.password = hashed_password.decode('utf-8')

    db.commit()
    db.refresh(user)

    return {"message": "Şifre başarıyla güncellendi."}

@router.get("/class/{class_id}/students", dependencies=[Depends(teacher_only)])
def get_students_by_class(class_id: int, db: Session = Depends(get_db)):
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

