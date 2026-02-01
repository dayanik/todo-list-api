from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import DATABASE_URL
from app import models, utils, schemas, exceptions


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
async def create_user(
        data: schemas.UserRegisterRequest, session: AsyncSession
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
        raise exceptions.HTTPEmailNotUniqueException()


@connection
async def get_user(email: str, session: AsyncSession) -> models.User:
    query = select(models.User).where(models.User.email == email)
    user_row = await session.execute(query)
    return user_row.scalar_one_or_none()


@connection
async def create_task(
        data: schemas.TaskRequest, 
        user_id: int, 
        session: AsyncSession
    ) -> models.Task:
    
    task = models.Task(**data.model_dump())
    task.user_id = user_id
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@connection
async def get_all_tasks(
    user_id,
    page: int,
    limit: int,
    session: AsyncSession) -> list[models.Task]:
    query = select(
        models.Task).where(
            models.Task.user_id == user_id).order_by(
                models.Task.updated_at).limit(
                    limit).offset(
                        (page - 1) * limit)
    result = await session.execute(query)
    tasks = result.scalars().all()
    return tasks


@connection
async def get_tasks_count(limit: int, session: AsyncSession):
    count_query = select(func.count()).select_from(models.Task)
    total_tasks = await session.scalar(count_query)
    return total_tasks


@connection
async def get_task(
      task_id: int, 
      session: AsyncSession
      ) -> models.Task | None:
    query = select(models.Task).where(models.Task.task_id == task_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


@connection
async def update_task(
        task_id: int, 
        data: schemas.TaskRequest,
        session: AsyncSession
    ) -> models.Task:
    
    query = select(models.Task).where(models.Task.task_id == task_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if not task:
         raise exceptions.HTTPTaskNotExistsException()
    
    task.title = data.title
    task.description = data.description
    await session.commit()
    
    return task


@connection
async def delete_task(
     task_id: int, 
     session: AsyncSession,
     ):
    query = select(models.Task).where(models.Task.task_id == task_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()
    if not task:
         raise exceptions.HTTPTaskNotExistsException()
    await session.delete(task)
    await session.commit()
