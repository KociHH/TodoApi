from pydantic import BaseModel


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