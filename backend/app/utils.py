import jwt

from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, status, Response, Request, Depends, status
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from typing import Annotated

from app import database, models, config


password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class HTTPEmailNotUniqueException(HTTPException):
    def __init__(
            self, 
            detail: str="User with than email is already exist", 
            headers: dict={"WWW-Authenticate": "Bearer"}
            ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT, 
            detail=detail, 
            headers=headers)


class HTTPTodoNotExistsException(HTTPException):
    def __init__(
            self, 
            detail: str="Task with that id not found", 
            headers: dict={"WWW-Authenticate": "Bearer"}
            ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=detail, 
            headers=headers)


class HTTPUnauthorizedException(HTTPException):
    def __init__(
            self, 
            detail: str="Could not validate credentials", 
            headers: dict={"WWW-Authenticate": "Bearer"}
            ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=detail, 
            headers=headers)


def verify_password(plain_pswd, hashed_pswd):
    return password_hash.verify(plain_pswd, hashed_pswd)


def get_password_hash(password):
    return password_hash.hash(password)


async def authenticate_user(email: str, password: str):
    user = await database.get_user(email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)]) -> models.User:
    try:
        payload = jwt.decode(
            token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPUnauthorizedException()
        token_data = models.TokenData(email=email)
    except InvalidTokenError:
        raise HTTPUnauthorizedException()
    user = await database.get_user(email=token_data.email)
    if user is None:
        raise HTTPUnauthorizedException()
    return user
