from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os
from app.database import SessionLocal, Base, engine
from app.models import User

app = FastAPI()

load_dotenv()

# --- CONFIG ---
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
SQLALCHEMY_DATABASE_URL = os.getenv("POSTGRES_URL")

# --- Create Table ---
Base.metadata.create_all(bind=engine)

# --- AUTH with Bcrypt ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def require_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user

# --- ROUTES ---
@app.post("/register")
def register(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == form_data.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    user = User(username=form_data.username, hashed_password=get_password_hash(form_data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"msg": "User created successfully"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "role": current_user.role}

@app.get("/admin")
def admin_only(current_admin: User = Depends(require_admin)):
    return {"msg": f"Welcome admin {current_admin.username}"}
