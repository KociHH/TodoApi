from fastapi.routing import JSONResponse
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
import logging
from contextlib import asynccontextmanager
from app.backend.db.sql.tables import dbase
from app.backend.db.sql.settings import engine
from jose import ExpiredSignatureError, jwt
from jose.exceptions import JWTError
from app.backend.api.security import tokens
from app.backend.api import auth, todo
from config import SECRET_KEY_JWT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(dbase.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def check_access_token(request: Request, call_next):
    public_paths = ["/login", "/register", '/']
    if any(request.url.path.startswith(p) for p in public_paths):
        responce = await call_next(request)
        return responce
    
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]

    if token:    
        try:
            payload: dict = jwt.decode(token, SECRET_KEY_JWT, )
            user_id = payload.get("user_id")
            request.state.user_id = user_id
        except (ExpiredSignatureError, JWTError) as e:
            logger.warning(f"Ошибка в функции access_token_middleware:\n {e}")
            request.state.user_id = None
            raise JSONResponse(status_code=500, content={"detail": "Недействительный access токен"})

        if not getattr(request.state, "user_id", None):
            return JSONResponse(status_code=401, content={"detail": "Не аутентифицирован"})

    responce = await call_next(request)
    return responce

app.mount("/static", StaticFiles(directory="app/frontend/dist/ts"))
app.route(auth.router)
app.route(todo.router)
app.mount(tokens.router)

if __name__ == "__main__":
    uvicorn.run("main:app")