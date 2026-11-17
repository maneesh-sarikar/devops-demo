
from contextlib import asynccontextmanager
import os

import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


def get_db():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "devdb"),
        user=os.getenv("DB_USER", "devuser"),
        password=os.getenv("DB_PASSWORD", "devpass123"),
        row_factory=dict_row
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                completed BOOLEAN DEFAULT FALSE
            )
        """)
    yield


app = FastAPI(
    title="DevOps Demo API",
    description="Containerized FastAPI and PostgreSQL application",
    version="1.0.0",
    lifespan=lifespan
)


class TaskCreate(BaseModel):
    title: str
    description: str = ""


class TaskUpdate(BaseModel):
    title: str
    description: str = ""
    completed: bool = False


@app.get("/")
def home():
    return {
        "message": "DevOps Demo API is running!",
        "status": "healthy"
    }


@app.get("/db-check")
def database_check():
    try:
        with get_db() as conn:
            database = conn.execute(
                "SELECT current_database()"
            ).fetchone()["current_database"]

        return {"database": database, "status": "connected"}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/tasks")
def create_task(task: TaskCreate):
    with get_db() as conn:
        result = conn.execute(
            """
            INSERT INTO tasks (title, description)
            VALUES (%s, %s)
            RETURNING *
            """,
            (task.title, task.description)
        ).fetchone()

    return result


@app.get("/tasks")
def get_tasks():
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM tasks ORDER BY id"
        ).fetchall()


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    with get_db() as conn:
        result = conn.execute(
            """
            UPDATE tasks
            SET title = %s, description = %s, completed = %s
            WHERE id = %s
            RETURNING *
            """,
            (task.title, task.description, task.completed, task_id)
        ).fetchone()

    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return result


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    with get_db() as conn:
        result = conn.execute(
            "DELETE FROM tasks WHERE id = %s RETURNING id"
            , (task_id,)
        ).fetchone()

    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"message": "Task deleted", "id": task_id}
