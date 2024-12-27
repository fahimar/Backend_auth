from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import models
import schemas
from database import get_db
import service
import logging

app = FastAPI()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@app.post("/signup/", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
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
            "username": db_user.username,
            "email": db_user.email,  # Include email in the response
            "id": db_user.id       # Include id in the response
        }
    except IntegrityError as e:
        logger.exception("An error occurred during signup:")
        db.rollback()  # Rollback the transaction in case of integrity error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error") from e
    except Exception as e:
        logger.exception("An error occurred during signup:")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error") from e


@app.post("/token/")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        logger.debug("Authenticating user...")
        db_user = await service.authenticate(db, form_data.username, form_data.password)
        if not db_user:
            logger.warning("Invalid credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        logger.debug("Generating access token...")
        access_token = await service.create_access_token(db_user.id, db_user.username)

        logger.info(f"User {form_data.username} authenticated successfully.")
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        logger.exception("An error occurred during login:")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error") from e


@app.get("/profile/", response_model=schemas.User)
async def get_current_user(token: str, db: Session = Depends(get_db)):
    try:
        db_user = await service.get_current_user(db, token)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return db_user
    except Exception as e:
        logger.exception("An error occurred during profile retrieval:")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error") from e