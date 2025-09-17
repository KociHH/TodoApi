from fastapi import FastAPI, Depends, HTTPException, APIRouter
import logging

from fastapi.responses import HTMLResponse
from app.backend.utils.dependencies import path_html

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def root_user():
    with open(path_html + "root.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    return HTMLResponse(content=html_content)