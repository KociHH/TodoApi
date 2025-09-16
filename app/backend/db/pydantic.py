from pydantic import BaseModel

class Register(BaseModel):
    password: int
    name: str

class Login(BaseModel):
    password: int
    name: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class EventTokensResponse(BaseModel):
    refresh_token: str | None
    access_toke: str | None
    token_type: str

class NewCreateTask(BaseModel):
    title: str
    description: str

class DeleteTask(BaseModel):
    task_id: int | str

class ChangeStatusTask(BaseModel):
    task_id: str | int

class ChangeTask(BaseModel):
    title: str
    description: str
    task_id: str | int