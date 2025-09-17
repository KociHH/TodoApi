from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
import logging
from config import ALGORITHM, SECRET_KEY_JWT, exp_access_token, exp_refresh_token
from typing import Any
from jose import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
logger = logging.getLogger(__name__)

class TokenProcess:
    def __init__(
        self,
        token: str | None = None,
        ) -> None:
        self.token = token
        self.data_token: None | dict = None

    def __call__(self) -> Any:
        return self.token_info()

    def verify_token(self, type: str) -> dict | None:
        token = None
        try:
            token = jwt.decode(self.token, SECRET_KEY_JWT, ALGORITHM)
        except JWTError as e:
            logger.error(f"Истек токен: {e}")
            raise HTTPException(status_code=401, detail=f"Token has expired: {type}")
        return token
    
    def token_info(self, token: str = Depends(oauth2_scheme)) -> Any:
        tp = TokenProcess(token)
        token_data = tp.verify_token(token)
        
        if token_data:
            self.token_data = token_data
            self.token = token

        return self.token_data, self.token

    def return_token_items(self, items: list[str] = ['user_id']) -> None | dict:
        if not self.token_data:
            logger.error(f"Не заданна переменная token_data: {self.token_data}")
            return

        for i in items:
            if i not in list(self.data_token.keys()):
                logger.error(f"Элемент {i} не найден в data_token: {self.data_token}")
                return

        result_return = {}
        for i in items:
            for k, v in self.data_token.items():
                if i == k:
                    result_return[k] = v

        if not result_return:
            logger.error("В result_return не было ничего добавленно")
            return

        return result_return
