from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_URL = "sqlite:///./data/OrderManager.db"

engine = create_engine(DB_URL, connect_args={"check_same_thread": False}) # управляет подключениями к бд, хранит пул подключений
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False) # фабрика сессий, создает сессии
Base = declarative_base() # базовый класс для всех таблиц, от него наследуются все классы в models

def get_db():
    db = SessionLocal() # создаем сессию
    try:
        yield db # отдаем сессию в эндпоинт
    finally:
        db.close() # закрываем сессию 
    