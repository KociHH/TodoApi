from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.responses import HTMLResponse
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from app.backend.schemas.user import Login, Register
from app.backend.db.sql.settings import get_db_session
from app.backend.db.sql.tables import UserRegistered
from app.backend.services.jwt.token import TokenProcess
from app.backend.utils.dependencies import PSWD_context, path_html
import logging
from app.backend.services.jwt.utils import create_token

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/register", response_class=HTMLResponse)
async def register_user():
    with open(path_html + "register.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    return HTMLResponse(content=html_content)

@router.post("/register")
async def register_process(reg: Register, db_session: AsyncSession = Depends(get_db_session)):
    user_dao = BaseDAO(UserRegistered, db_session)
    if await user_dao.get_one(UserRegistered.name == reg.name):
        return {
            "success": False,
            "message": "Этот никнейм занят",
        }

    pass_hash = PSWD_context.hash(reg.password)
    create = await user_dao.create({
        "password": pass_hash,
        "name": reg.name,
    })

    if not create:
        raise HTTPException(status_code=500, detail="System error: not added in db")

    access_token = create_token({"user_id": create.user_id}, "access")
    refresh_token = create_token({"user_id": create.user_id}, "refresh")

    logger.info(f"Новый пользователь был зарегестрирован: {reg.name}")
    return {
        "success": True,
        "message": "Успешная регистрация!",
        "access_token": access_token,
        "refresh_token": refresh_token  
    }


@router.get("/login", response_class=HTMLResponse)
async def login_user():
    with open(path_html + "login.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    return HTMLResponse(content=html_content)

@router.post("/login")
async def login_process(log: Login, db_session: AsyncSession = Depends(get_db_session)):
    user_dao = BaseDAO(UserRegistered, db_session)
    user = await user_dao.get_one(UserRegistered.name == log.name)

    if user:
        pass_hash = PSWD_context.verify(log.password, user.password)

        if pass_hash:
            access_token = create_token({"user_id": user.user_id}, "access")
            refresh_token = create_token({"user_id": user.user_id}, "refresh")
            
            logger.info(f"Пользователь {user.user_id} зашел в аккаунт.")
            return {
                "success": True,
                "message": "Успешная авторизация!",
                "access_token": access_token,
                "refresh_token": refresh_token
            }
        else:
            return {
                "success": False,
                "message": "Неверный пароль"
            }

    else:
        return {
            'success': False,
            "message": f"Пользователь с ником {log.name} не найден."
        }