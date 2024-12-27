from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from database import get_db
import models
from schemas import UserCreate

SECRET_KEY = "mysecretkey"
EXPIRE_MINUTES = 60 * 24
ALGORITHM = "HS256"

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")
bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def existing_user(db: Session, username: str, email: str):
    result = await db.execute(select(models.User).where(models.User.username == username))  # Use 'select'
    db_user = result.scalars().first()
    if db_user:
        return db_user

    result = await db.execute(select(models.User).where(models.User.email == email))  # Use 'select'
    db_user = result.scalars().first()
    if db_user:
        return db_user
    return None

#create token
async def create_access_token(id: int, username: str):
    encode = {"sub": username, "id": id}
    expires = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

# GET CURRENT USER FROM TOKEN

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        id: int = payload.get("id")
        expires: datetime = payload.get("exp")
        if expires < datetime.utcnow():
            return None
        if username is None or id is None:
            return None
        db_user = db.query(models.User).filter(models.User.id == id).first()
        return db_user
    except JWTError:
        return None

# create user
async def create_user(db: Session, user: UserCreate):
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=bcrypt.hash(user.password)  # Use bcrypt.hash directly
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user