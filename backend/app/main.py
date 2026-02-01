import jwt
import math

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


@app.exception_handler(HTTPException)
async def validation_exception_handler(
    request: Request, exc: HTTPException):
    return JSONResponse(content=exc.detail, status_code=exc.status_code)


@app.post(
        "/register",
        response_model=models.Token,
        status_code=status.HTTP_201_CREATED
        )
async def create_user(data: models.UserRegisterRequest):
    user: models.User = await database.create_user_on_db(data)
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return models.Token(access_token=access_token, token_type="Bearer")


@app.post("/login", response_model=models.Token)
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
    return models.Token(access_token=access_token, token_type="Bearer")


@app.get("/todos/{todo_id}", response_model=models.TodoGetModel)
async def get_todo(
    todo_id: int, 
    user: Annotated[models.User, Depends(utils.get_current_user)]
    ):
    todo = await database.get_todo_from_db(todo_id)
    if not todo:
        raise utils.HTTPTodoNotExistsException()
    return todo


@app.get("/todos", response_model=models.TodoListGetModel)
async def get_all_todos(
    user: Annotated[models.User, Depends(utils.get_current_user)],
    page: int=1, limit: int=10
    ):
    todos = await database.get_all_todos_from_db(user.user_id, page, limit)
    todos_count = await database.get_todos_count(limit)
    todos_response = models.TodoListGetModel(
        data=todos,
        limit=limit,
        page=page,
        total=math.ceil(todos_count / limit)
    )
    return todos_response


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    user: Annotated[models.User, Depends(utils.get_current_user)]):
    await database.delete_todo_from_db(todo_id)


@app.post(
        "/todos",
        response_model=models.TodoGetModel, 
        status_code=status.HTTP_201_CREATED)
async def create_todos(
    data: models.TodoRequest,
    user: Annotated[models.User, Depends(utils.get_current_user)]
    ):
    todo = await database.create_todo_on_db(data, user.user_id)
    return todo


@app.put("/todos/{todo_id}", response_model=models.TodoGetModel)
async def update_todo(
    todo_id: int, 
    data: models.TodoRequest,
    user: Annotated[models.User, Depends(utils.get_current_user)]
    ):
    todo = await database.update_todo_on_db(todo_id, data)
    return todo
