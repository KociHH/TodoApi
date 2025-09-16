from fastapi import APIRouter, HTTPException, Request
import logging
from app.backend.jwt.utils import create_token
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.backend.jwt.token import TokenProcess
from app.backend.db.sql.settings import get_db_session
from app.backend.db.pydantic import RefreshTokenRequest, EventTokensResponse
from datetime import timedelta
from app.backend.utils.dependencies import curretly_msk
from jose.exceptions import ExpiredSignatureError, JWTError

sistem_error = "Server error"
router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/refresh", response_model=EventTokensResponse)
async def refresh_access_update(
    request_body: RefreshTokenRequest, 
    token_info: TokenProcess = Depends(TokenProcess().token_info)
    ):
    try:
        token_info.token = request_body.refresh_token

        token = token_info.verify_token("refresh")
        if not token:
            logger.error('Не вернулось значение функции verify_token')
            raise HTTPException(status_code=500, detail=sistem_error)

        user_id_refresh = token.get("user_id")

        new_access_token, _ = create_token(data={"user_id": user_id_refresh}, type="access")
        new_refresh_token, new_jti = create_token(data={"user_id": user_id_refresh}, type="refresh")

        if not any(new_access_token and new_refresh_token and new_jti):
            logger.error("Не вернулось значение (create_access_token, create_refresh_token)")
            raise HTTPException(status_code=500, detail=sistem_error)

        return {
            "access_token": new_access_token, 
            "refresh_token": new_refresh_token, 
            "token_type": "refresh"
            }
    except HTTPException as e:
        raise e
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expire")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    except Exception as e:
        logger.error(f"Ошибка при обновлении токена: {e}")
        raise HTTPException(status_code=500, detail=sistem_error)

@router.post("/access", response_model=EventTokensResponse)
async def access_update(
    request_body: RefreshTokenRequest,
    token_info: TokenProcess = Depends(TokenProcess().token_info)
    ):
    try:
        token_info.token = request_body.refresh_token

        token = token_info.verify_token("refresh")
        if not token:
            logger.error('Не вернулось значение функции verify_refresh_token')
            raise HTTPException(status_code=500, detail=sistem_error)
    
        user_id = token.get('user_id')
        access_token = create_token(data={"user_id": user_id}, type="access")

        if not access_token:
            logger.error("Не вернулось значение (create_token)")
            raise HTTPException(status_code=500, detail=sistem_error)
    
        return {
            "access_token": access_token, 
            "refresh_token": None,
            "token_type": "access",
            } 
    except HTTPException as e:
        raise e
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expire")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    except Exception as e:
        logger.error(f'Внезапная ошибка в функции access_update:\n {e}')
        raise HTTPException(status_code=500, detail=sistem_error) 

@router.post("/check_update_tokens")    
async def check_update_tokens(
    token_info: TokenProcess = Depends(TokenProcess().token_info)
):
    user_id = token_info.data_token.get("user_id")

    try:
        return {
            "success": True,
            "user_id": user_id,
            "message": "Token is valid"
        }
    except Exception as e:
        logger.error(f"Не валидный токен либо другое: {e}")
        raise HTTPException(status_code=401, detail="Token validation failed")



