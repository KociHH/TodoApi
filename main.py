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
from app.backend.api import auth, todo, root
from app.backend.services.limits import limiter
from config import SECRET_KEY_JWT
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(dbase.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def ratelimit_handler(request: Request, exc: RateLimitExceeded):
    headers = {
        "Retry-After": "10",
        "X-RateLimit-Limit": "60",
        "X-RateLimit-Remaining": "0",
    }
    return JSONResponse(status_code=429, content={"detail": "Too Many Requests"}, headers=headers)

app.add_middleware(SlowAPIMiddleware)

@app.middleware("http")
async def check_access_token(request: Request, call_next):
    public_paths = ["/login", "/register", '/']
    if any(request.url.path.startswith(p) for p in public_paths):
        response = await call_next(request)
        return response

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
            raise HTTPException(status_code=401, detail="Invalid access token")

        if not getattr(request.state, "user_id", None):
            return HTTPException(status_code=401, detail="User not authenticated")

    response = await call_next(request)
    return response

app.mount("/static", StaticFiles(directory="app/frontend/dist/ts"))
app.include_router(auth.router)
app.include_router(todo.router)
app.include_router(tokens.router)
app.include_router(root.router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)