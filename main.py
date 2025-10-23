from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session  # ← исправлено "orn" на "orm"
from typing import Optional
from datetime import datetime  # ← добавьте этот импорт

from database import get_db
from models import User, Base, engine
from schemas import UserLogin, VerifyCode, Token, SMSResponse
from auth import create_access_token, verify_token
from msg_ovrx import msg_ovrx_service

# Создаем таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SMS Auth API", version="1.0.0")


@app.post("/auth/otp", response_model=SMSResponse)
async def send_otp(
        user_data: UserLogin,
        db: Session = Depends(get_db)
):
    """Отправка SMS с кодом подтверждения"""

    if not user_data.email and not user_data.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Укажите email или телефон"
        )

    # Ищем пользователя
    query = db.query(User)
    if user_data.email:
        user = query.filter(User.email == user_data.email).first()
    else:
        user = query.filter(User.phone == user_data.phone).first()

    # Если пользователь не найден, создаем нового
    if not user:
        user = User(
            email=user_data.email,
            phone=user_data.phone
        )
        db.add(user)

    # Генерируем код подтверждения
    code = user.generate_verification_code()
    db.commit()

    # Отправляем SMS (если указан телефон)
    if user.phone:
        message = f"Ваш код подтверждения: {code}"
        sms_response = await msg_ovrx_service.send_sms(user.phone, message)

        if not sms_response.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=sms_response.message
            )

        return sms_response
    else:
        # Для email можно реализовать отправку письма
        return SMSResponse(
            success=True,
            message=f"Код подтверждения: {code} (реализуйте отправку email)"
        )


@app.post("/auth/verify", response_model=Token)
async def verify_code(
        verify_data: VerifyCode,
        db: Session = Depends(get_db)
):
    """Проверка кода подтверждения"""

    if not verify_data.email and not verify_data.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Укажите email или телефон"
        )

    # Ищем пользователя
    query = db.query(User)
    if verify_data.email:
        user = query.filter(User.email == verify_data.email).first()
    else:
        user = query.filter(User.phone == verify_data.phone).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    # Проверяем код
    if not user.is_code_valid():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Код истек или не был запрошен"
        )

    if user.verific_code != verify_data.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный код подтверждения"
        )

    # Обновляем пользователя
    user.verific_code = None
    user.code_expires = None
    user.is_verified = True
    user.last_login = datetime.utcnow()
    db.commit()

    # Создаем токен
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "phone": user.phone}
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        phone=user.phone
    )


@app.get("/users/me")
async def read_users_me(
        token: str = Depends(verify_token),
        db: Session = Depends(get_db)
):
    """Получение информации о текущем пользователе"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен"
        )

    user = db.query(User).filter(User.id == token.get("sub")).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    return {
        "id": user.id,
        "email": user.email,
        "phone": user.phone,
        "is_verified": user.is_verified,
        "last_login": user.last_login
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)