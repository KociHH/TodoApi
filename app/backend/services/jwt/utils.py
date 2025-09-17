from datetime import timedelta, datetime
import uuid
from jose import jwt
import logging
from config import ALGORITHM, SECRET_KEY_JWT, exp_access_token, exp_refresh_token
from app.backend.utils.dependencies import curretly_msk

logger = logging.getLogger(__name__)


def create_token(
    data: dict, 
    type: str, 
    exp: datetime | None = None,
    ) -> str | None:        
    if type == "access":   
        if not exp:
            exp_result =  curretly_msk() + timedelta(minutes=exp_access_token)
    elif type == "refresh":
        if not exp:
            exp_result =  curretly_msk() + timedelta(days=exp_refresh_token)
    elif exp == None:
        logger.error(f"Не задан аргумент exp: {exp} для {type} токена")
        return

    data['jti'] = str(uuid.uuid4())
    data["exp"] = exp_result
    data['type'] = type

    return jwt.encode(data, SECRET_KEY_JWT, ALGORITHM)