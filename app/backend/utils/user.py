from fastapi import Depends
from app.backend.jwt.token import TokenProcess, oauth2_scheme
from typing import Any

class UserProcess:
    def __init__(
        self,
        user_id: str | int
        ) -> None:
        self.user_id = user_id
        self.token_data = None


