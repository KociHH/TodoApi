from typing import Coroutine
from fastapi import Depends, APIRouter, HTTPException
from fastapi.params import Query
import logging
from fastapi.responses import HTMLResponse
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_

from app.backend.schemas.todo import ChangeStatusTask, ChangeTask, DeleteTask, NewCreateTask
from app.backend.db.sql.settings import get_db_session
from app.backend.db.sql.tables import TodoElements, UserRegistered
from app.backend.services.jwt.token import TokenProcess
from app.backend.utils.dependencies import path_html

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/todo/tasks", response_class=HTMLResponse)
async def tasks_user():
    with open(path_html + "todo/tasks.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    return HTMLResponse(content=html_content)

@router.get("/todo/tasks/data")
async def tasks_data_user(
    token_info: TokenProcess = Depends(TokenProcess().token_info),
    db_session: AsyncSession = Depends(get_db_session)
    ):
    token_data, _ = token_info
    user_id = token_data.get("user_id")
    
    user_dao = BaseDAO(TodoElements, db_session)
    user = await user_dao.get_all_column_values(
        columns=(
            TodoElements.title,
            TodoElements.description, 
            TodoElements.status, 
            TodoElements.id_todo, 
            ),
        where=TodoElements.user_id == user_id)

    if user:
        user.sort(key=lambda i: i[3])
        if len(user) > 10:
            user = user[:10]
        
        tasks_to_list = []
        for task_tuple in user:
            tasks_to_list.append({
                "title": task_tuple[0],
                "description": task_tuple[1],
                "status": task_tuple[2],
                "id_todo": task_tuple[3]
            })

        return {
            "success": True,
            "todo": tasks_to_list,
        }
    
    else:
        return {
            "success": False,
            "todo": (),
        }


@router.get("/todo/create", response_class=HTMLResponse)
async def create_task_user():
    with open(path_html + "todo/create.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    return HTMLResponse(content=html_content)

@router.post("/todo/create")
async def create_task_post(
    newtask: NewCreateTask,
    token_info: TokenProcess = Depends(TokenProcess().token_info),
    db_session: AsyncSession = Depends(get_db_session)
):
    token_data, _ = token_info
    user_id = token_data.get("user_id")
    task_dao = BaseDAO(TodoElements, db_session)

    tasks_id = await task_dao.get_all_column_values(
        columns=TodoElements.id_todo,
        where=TodoElements.user_id == user_id
    )

    if tasks_id:
        for existing_task_id in sorted(tasks_id, reverse=True):
            await task_dao.update(
                and_(TodoElements.id_todo == existing_task_id,
                TodoElements.user_id == user_id),
                {"id_todo": existing_task_id + 1}
            )
    await task_dao.create({
        "title": newtask.title,
        "description": newtask.description,
        "status": False,
        "id_todo": 1,
        "user_id": user_id
    })

    logger.info(f"Добавлена таска юзером: {user_id}")
    return {
        "success": True,
        "message": "Task addition!"
    }


@router.post("/todo/delete")
async def delete_task_post(
    delete_task: DeleteTask,
    token_info: TokenProcess = Depends(TokenProcess().token_info),
    db_session: AsyncSession = Depends(get_db_session)
):
    try:
        task_dao = BaseDAO(TodoElements, db_session)
        token_data, _ = token_info
        user_id = token_data.get("user_id")
        delete_task_id_int = int(delete_task.task_id)

        where = and_(
            TodoElements.user_id == user_id,
            TodoElements.id_todo == delete_task_id_int,
            )

        tasks_id = await task_dao.get_all_column_values(
            columns=TodoElements.id_todo,
            where=TodoElements.user_id == user_id
        )

        if tasks_id:
            deleted = await task_dao.delete(where)

            if deleted:
                for existing_task_id in sorted(tasks_id, reverse=True):
                    await task_dao.update(
                    where,
                    {"id_todo": existing_task_id - 1},
                )

                logger.info(f"Удалена таска юзером: {user_id}")
                return {
                    "success": True,
                    "message": "Task successfully removed!"
                }
        return {
            "success": False,
            "message": "System error"            
        }

    except Exception as e:      
        logger.error(f"Ошибка в функции delete_task_post: {e}")
        raise HTTPException(status_code=500, detail="System error")


@router.post("/todo/change_status")
async def change_status_task_post(
    status_task: ChangeStatusTask,
    token_info: TokenProcess = Depends(TokenProcess().token_info),
    db_session: AsyncSession = Depends(get_db_session)
):
    try:
        task_dao = BaseDAO(TodoElements, db_session)
        token_data, _ = token_info
        user_id = token_data.get("user_id")
        status_task_id_int = int(status_task.task_id)

        where = and_(
            TodoElements.user_id == user_id,
            TodoElements.id_todo == status_task_id_int,
        )

        task_info = await task_dao.get_one(where)
        old_status = task_info.status
        new_status = not old_status

        if task_info:
            updated = await task_dao.update(
                where,
                {"status": new_status}
            )
        
            if updated:
                logger.info(f"Изменен статус таски {status_task.task_id} на {new_status} юзером: {user_id}")
                return {
                    "success": True,
                    "message": "Status updated!",
                }

        return {
            "success": False,
            "message": "System error"            
        }

    except Exception as e:      
        logger.error(f"Ошибка в функции change_status_task_post: {e}")
        raise HTTPException(status_code=500, detail="System error")


@router.get("/todo/change", response_class=HTMLResponse)
async def change_task():
    with open(path_html + "todo/change.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    html_content = html_content.replace("{{title}}", "")
    html_content = html_content.replace("{{description}}", "")

    return HTMLResponse(content=html_content)

@router.get("/todo/data/change")
async def change_data_task(
    task_id: str | int = Query(..., description="Получение task_id"),
    token_info: TokenProcess = Depends(TokenProcess().token_info),
    db_session: AsyncSession = Depends(get_db_session)
):
    try:
        task_dao = BaseDAO(TodoElements, db_session)
        token_data, _ = token_info
        user_id = token_data.get("user_id")
        task_id_int = int(task_id)

        where = and_(
            TodoElements.user_id == user_id,
            TodoElements.id_todo == task_id_int,
        )

        task_info = await task_dao.get_one(where)

        if task_info:
            return {
                "success": True,
                "title": task_info.title,
                "description": task_info.description,
                "task_id": task_id
            }
        
        return {
                "success": False,
                "title": "",
                "description": "",
                "task_id": task_id
            }

    except Exception as e:      
        logger.error(f"Ошибка в функции change_data_task: {e}")
        raise HTTPException(status_code=500, detail="System error")

@router.post("/todo/change")
async def change_task_post(
    change_task: ChangeTask,
    token_info: TokenProcess = Depends(TokenProcess().token_info),
    db_session: AsyncSession = Depends(get_db_session)
):
    try:
        task_dao = BaseDAO(TodoElements, db_session)
        token_data, _ = token_info
        user_id = token_data.get("user_id")
        change_task_id_int = int(change_task.task_id)
        
        where = and_(
            TodoElements.user_id == user_id,
            TodoElements.id_todo == change_task_id_int,
        )

        updated = await task_dao.update(
            where,
            {
                "title": change_task.title,
                "description": change_task.description
            })

        if updated:
            logger.info(f"Изменена таска {change_task.task_id} юзером: {user_id}")
            return {
                "success": True,
                "message": f"Task {change_task.task_id} was updated!"
            }
            
        return {
            "success": False,
            "message": "System error"
        }

    except Exception as e:      
        logger.error(f"Ошибка в функции change_task_post: {e}")
        raise HTTPException(status_code=500, detail="System error")