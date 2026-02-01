import math

from datetime import timedelta
from fastapi import FastAPI, status, Response, Request, Depends
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from typing import Annotated

from app import database, models, config, utils, schemas, exceptions


# инициализация приложения с базой данных
app = FastAPI(lifespan=database.lifespan)


# общий обработчик исключения валидации длинной ссылки
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
    return Response(status_code=status.HTTP_400_BAD_REQUEST)


@app.exception_handler(HTTPException)
async def validation_exception_handler(
        request: Request, exc: HTTPException
    ):
    return JSONResponse(content=exc.detail, status_code=exc.status_code)


@app.post(
        "/register",
        response_model=schemas.Token,
        status_code=status.HTTP_201_CREATED
    )
async def create_user(data: schemas.UserRegisterRequest):
    user = await database.create_user(data)
    token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils.create_access_token(
        data={"sub": user.email},
        expires_delta=token_expires
    )
    return schemas.Token(access_token=access_token, token_type="Bearer")


@app.post("/login", response_model=schemas.Token)
async def login_user(data: schemas.UserLoginRequest):
    user = await utils.authenticate_user(
            email=data.email,
            password=data.password
        )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW_Authenticate": "Bearer"},
        )
    token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils.create_access_token(
        data={"sub": user.email},
        expires_delta=token_expires
    )
    return schemas.Token(access_token=access_token, token_type="Bearer")


@app.post(
        "/todos",
        response_model=schemas.TaskGetModel, 
        status_code=status.HTTP_201_CREATED
    )
async def create_task(
        data: schemas.TaskRequest,
        user: Annotated[models.User, Depends(utils.get_current_user)]
    ):
    task = await database.create_task(data, user.user_id)
    return task


@app.get("/todos", response_model=schemas.TaskListGetModel)
async def get_all_tasks(
        user: Annotated[schemas.UserInDB, Depends(utils.get_current_user)],
        page: int=1, limit: int=10
    ):
    tasks = await database.get_all_tasks(user.user_id, page, limit)
    tasks_count = await database.get_tasks_count()
    tasks_response = schemas.TaskListGetModel(
        data=tasks,
        limit=limit,
        page=page,
        total=math.ceil(tasks_count / limit)
    )
    return tasks_response


@app.get("/todos/{task_id}", response_model=schemas.TaskGetModel)
async def get_task(
        task_id: int, 
        user: Annotated[schemas.UserInDB, Depends(utils.get_current_user)]
    ):
    task = await database.get_task(task_id)
    if not task:
        raise exceptions.HTTPTaskNotExistsException()
    return task


@app.put("/todos/{task_id}", response_model=schemas.TaskGetModel)
async def update_task(
        task_id: int, 
        data: schemas.TaskRequest,
        user: Annotated[schemas.UserInDB, Depends(utils.get_current_user)]
    ):
    task = await database.update_task(task_id, data)
    return task

@app.delete("/todos/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
        task_id: int,
        user: Annotated[schemas.UserInDB, Depends(utils.get_current_user)]
    ):
    await database.delete_task(task_id)
