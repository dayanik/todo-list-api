from fastapi import FastAPI, status, Response, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app import database
from app.models import TodoRequest, UserRequest


# инициализация приложения с базой данных
app = FastAPI(lifespan=database.lifespan)


# общий обработчик исключения валидации длинной ссылки
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return Response(status_code=status.HTTP_400_BAD_REQUEST)


@app.post("/register")
@app.post("/")
async def create_user(data: UserRequest):
    token = await database.create_user_on_db(data)
    return JSONResponse(content=token, status_code=status.HTTP_201_CREATED)


@app.post("/login")
async def login_user(data: UserRequest):
    token = await database.login_user_on_db(data)
    return JSONResponse(content=token, status_code=status.HTTP_200_OK)


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
async def create_todos(data: TodoRequest):
    todo = await database.create_todo_on_db(data)
    return JSONResponse(content=todo, status_code=status.HTTP_201_CREATED)


@app.put("/todos/{todo_id}")
async def update_todo(todo_id: int, data: TodoRequest):
    todo = await database.update_todo_on_db(todo_id, data)
    if todo:
        return JSONResponse(content=todo, status_code=status.HTTP_200_OK)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
