from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# โหลด .env เพื่อใช้ค่า POSTGRES_URL
load_dotenv()

# ดึงค่าจาก .env เช่น: "postgresql://tum:secret123@localhost:5432/fastapi_db"
SQLALCHEMY_DATABASE_URL = os.getenv("POSTGRES_URL")

# สร้าง engine โดยไม่ต้องมี connect_args
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# สร้าง session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base class สำหรับ model ทั้งหมด
Base = declarative_base()
