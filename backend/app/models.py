from datetime import datetime
from sqlalchemy import String, Integer, JSON, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncAttrs


class UserRequest(BaseModel):
    name: str
    email: str
    password: str


class TodoRequest(BaseModel):
    title: str
    description: str


class TodoGetModel(BaseModel):
    id: int
    title: str
    description: str


class TodoListGetModel(BaseModel):
    data: list[TodoGetModel]
    page: int
    limit: int
    total: int


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    token: Mapped[str]
    todos: Mapped[list["Todo"]] = relationship(
        "Todo", back_populates='user', cascade="all, delete-orphan")


class Todo(Base):
    __tablename__ = "todos"

    todo_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str]
    user: Mapped["User"] = relationship("User", back_populates="todos")

    def to_dict(self) -> dict:
        return {
            'todo_id': self.post_id,
            'title': self.title,
            'description': self.content
        }
