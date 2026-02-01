from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None


class UserRegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class UserLoginRequest(BaseModel):
    email: str
    password: str


class UserInDB(BaseModel):
    user_id: int
    name: str
    email: str
    password: str


class TaskRequest(BaseModel):
    title: str
    description: str


class TaskGetModel(BaseModel):
    task_id: int
    title: str
    description: str

    model_config = ConfigDict(from_attributes=True)


class TaskListGetModel(BaseModel):
    data: list[TaskGetModel]
    page: int
    limit: int
    total: int
