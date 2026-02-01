from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import DATABASE_URL
from app import models, utils


engine = create_async_engine(DATABASE_URL)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield


# декоратор создания сессии
def connection(method):
	async def wrapper(*args, **kwargs):
		async with async_session_maker() as session:
			try:
				return await method(*args, session=session, **kwargs)
			except Exception as e:
				await session.rollback()
				raise e
			finally:
				await session.close()
	return wrapper


@connection
async def get_user(email: str, session: AsyncSession) -> models.User:
    query = select(models.User).where(models.User.email == email)
    user_row = await session.execute(query)
    return user_row.scalar_one_or_none()


@connection
async def create_user_on_db(
        data: models.UserRegisterRequest, session: AsyncSession
    ) -> models.User | None:
    user = models.User(**data.model_dump())
    user.password = utils.get_password_hash(user.password)
    session.add(user)
    try:
        await session.commit()
        await session.refresh(user)
        return user
    except IntegrityError:
        await session.rollback()
        raise utils.HTTPEmailNotUniqueException()


@connection
async def get_all_todos_from_db(
    user_id,
    page: int,
    limit: int,
    session: AsyncSession) -> list[models.Todo]:
    query = select(
        models.Todo).where(
            models.Todo.user_id == user_id).order_by(
                models.Todo.updated_at).limit(
                    limit).offset(
                        (page - 1) * limit)
    result = await session.execute(query)
    todos = result.scalars().all()
    return todos


@connection
async def get_todos_count(limit: int, session: AsyncSession):
    count_query = select(func.count()).select_from(models.Todo)
    total_todos = await session.scalar(count_query)
    return total_todos


@connection
async def get_todo_from_db(
      todo_id: int, 
      session: AsyncSession
      ) -> models.Todo | None:
    query = select(models.Todo).where(models.Todo.todo_id == todo_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


@connection
async def delete_todo_from_db(
     todo_id: int, 
     session: AsyncSession,
     ):
    query = select(models.Todo).where(models.Todo.todo_id == todo_id)
    result = await session.execute(query)
    todo = result.scalar_one_or_none()
    if not todo:
         raise utils.HTTPTodoNotExistsException()
    await session.delete(todo)
    await session.commit()


@connection
async def create_todo_on_db(
        data: models.TodoRequest, 
        user_id: int, 
        session: AsyncSession
    ) -> models.Todo:
    
    todo = models.Todo(**data.model_dump())
    todo.user_id = user_id
    session.add(todo)
    await session.commit()
    await session.refresh(todo)
    return todo


@connection
async def update_todo_on_db(
        todo_id: int, 
        data: models.TodoRequest,
        session: AsyncSession
    ) -> models.Todo:
    
    query = select(models.Todo).where(models.Todo.todo_id == todo_id)
    result = await session.execute(query)
    todo = result.scalar_one_or_none()

    if not todo:
         raise utils.HTTPTodoNotExistsException()
    
    todo.title = data.title
    todo.description = data.description
    await session.commit()
    
    return todo
