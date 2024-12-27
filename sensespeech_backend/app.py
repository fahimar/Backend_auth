from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import User as UserModel
from schemas import User as UserSchema, UserCreate
from database import get_db
import logging
import service

app = FastAPI()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.post("/signup/", status_code=status.HTTP_201_CREATED, response_model=UserSchema)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        logger.debug("Checking for existing user...")
        db_user = await service.existing_user(db, user.username, user.email)
        if db_user:
            logger.warning("User already exists")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists"
            )

        logger.debug("Creating new user...")
        db_user = await service.create_user(db, user)
        logger.debug("Generating access token...")
        access_token = await service.create_access_token(db_user.id, db_user.username)

        logger.info(f"User {user.username} created successfully.")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "username": db_user.username
        }
    except Exception as e:
        logger.exception("An error occurred during signup:")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")