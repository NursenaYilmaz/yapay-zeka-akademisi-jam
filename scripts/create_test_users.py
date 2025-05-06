import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def create_user(email: str, password: str, role: str):
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": email,
            "password": password,
            "role": role
        }
    )
    return response.json()

def login(email: str, password: str):
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": email,
            "password": password
        }
    )
    return response.json()

def main():
    # Test öğretmeni oluştur
    teacher = create_user(
        email="teacher@test.com",
        password="test123",
        role="teacher"
    )
    print("Öğretmen oluşturuldu:", teacher)

    # Test öğrencileri oluştur
    students = []
    for i in range(3):
        student = create_user(
            email=f"student{i+1}@test.com",
            password="test123",
            role="student"
        )
        students.append(student)
        print(f"Öğrenci {i+1} oluşturuldu:", student)

    # Öğretmen girişi yap
    teacher_login = login("teacher@test.com", "test123")
    print("\nÖğretmen girişi:", teacher_login)

    # Öğrenci girişleri yap
    print("\nÖğrenci girişleri:")
    for i in range(3):
        student_login = login(f"student{i+1}@test.com", "test123")
        print(f"Öğrenci {i+1} girişi:", student_login)

if __name__ == "__main__":
    main() 