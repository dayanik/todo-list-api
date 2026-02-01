import jwt

from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, status, Response, Request, Depends
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from typing import Annotated

from app import database, models, config, utils


# инициализация приложения с базой данных
app = FastAPI(lifespan=database.lifespan)


# общий обработчик исключения валидации длинной ссылки
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError):
    return Response(status_code=status.HTTP_400_BAD_REQUEST)


@app.exception_handler(utils.HTTPUnauthorizedException)
async def validation_exception_handler(
    request: Request, exc: utils.HTTPUnauthorizedException):
    return JSONResponse(content=exc.detail, status_code=status.HTTP_409_CONFLICT)


@app.exception_handler(HTTPException)
async def validation_exception_handler(
    request: Request, exc: HTTPException):
    return JSONResponse(content=exc.detail, status_code=status.HTTP_409_CONFLICT)


@app.post("/register")
async def create_user(data: models.UserRegisterRequest):
    user = await database.create_user_on_db(data)
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return JSONResponse(content=access_token, status_code=status.HTTP_201_CREATED)


@app.post("/login")
async def login_user(data: models.UserLoginRequest):
    user = await utils.authenticate_user(
        email=data.email, password=data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW_Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return JSONResponse(content=access_token, status_code=status.HTTP_200_OK)

'''
@app.get("/todos/")
@app.get("/todos")
async def get_all_todos(page: int=1, limit: int=10):
    posts = await database.get_all_todos_from_db()
    content = []
    return JSONResponse(content=content, status_code=status.HTTP_200_OK)


@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    todo = await database.delete_todo_from_db(todo_id)
    if todo:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@app.post("/todos")
async def create_todos(data: models.TodoRequest):
    todo = await database.create_todo_on_db(data)
    return JSONResponse(content=todo, status_code=status.HTTP_201_CREATED)


@app.put("/todos/{todo_id}")
async def update_todo(todo_id: int, data: models.TodoRequest):
    todo = await database.update_todo_on_db(todo_id, data)
    if todo:
        return JSONResponse(content=todo, status_code=status.HTTP_200_OK)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
'''