from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import httpx
import jwt
from datetime import datetime, timedelta

from app.database.database import supabase
from app.schemas.user_schemas import User
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer
from app.schemas.user_schemas import GoogleTokenRequest  # Імпортуємо схему

router = APIRouter()  # Замість auth_router використовується router


# OAuth2 схема
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)):
    """
    Створення JWT access токену за допомогою секрету з налаштувань
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")
    return encoded_jwt


@router.post("/auth/google")  # Ось це має бути тут
async def google_auth(request: GoogleTokenRequest):
    """
    Точка входу для Google OAuth аутентифікації
    """
    try:
        # Перевірка токену на Google
        async with httpx.AsyncClient() as client:
            google_response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={request.id_token}"
            )

        # Перевірка статусу відповіді
        if google_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid Google token")

        # Парсинг відповіді від Google
        token_info = google_response.json()

        # Додаткова перевірка Google Client ID (рекомендується)
        if token_info.get('aud') != settings.GOOGLE_CLIENT_ID:
            raise HTTPException(status_code=401, detail="Invalid Google Client ID")

        # Перевірка email
        if not token_info.get('email_verified'):
            raise HTTPException(status_code=401, detail="Email not verified")

        user_email = token_info.get('email')
        user_name = token_info.get('name', '')

        # Перевірка, чи існує користувач
        user_response = supabase.from_("User").select("*").eq("email", user_email).execute()

        # Якщо користувача немає, створюємо новий запис
        if not user_response.data:
            create_response = supabase.from_("User").insert({
                "email": user_email,
                "username": user_name,
                "google_id": token_info.get('sub')
            }).execute()

            if create_response.status_code != 201:
                raise HTTPException(status_code=500, detail="Failed to create user in database")

            # Створення нового користувача
            user_response = supabase.from_("User").select("*").eq("email", user_email).execute()

        # Створення access токену
        access_token = create_access_token(
            data={"sub": user_email},
            expires_delta=timedelta(minutes=60)
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_info": {
                "email": user_email,
                "username": user_name
            }
        }

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

# Потрібно додати цей router до головного додатку (main.py)
# Наприклад:
# app.include_router(router)
