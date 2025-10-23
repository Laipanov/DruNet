from sqlalchemy import Column, Integer, String, Boolean, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import uuid
import os

# Настройки базы данных (можно вынести в config.py)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./auth.db")

# Создаем engine
engine = create_engine(DATABASE_URL)

# Создаем SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=True)
    verific_code = Column(Integer, nullable=True)
    code_expires = Column(DateTime, nullable=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def is_code_valid(self):
        if not self.verific_code or not self.code_expires:
            return False
        return datetime.utcnow() < self.code_expires

    def generate_verification_code(self):
        import random
        self.verific_code = random.randint(100000, 999999)
        self.code_expires = datetime.utcnow() + timedelta(minutes=10)
        return self.verific_code


# Экспортируем engine для использования в main.py
__all__ = ['User', 'Base', 'engine', 'SessionLocal']