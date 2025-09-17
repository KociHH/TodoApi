from pydantic import BaseModel


class Register(BaseModel):
    password: str
    name: str

class Login(BaseModel):
    password: str
    name: str
    