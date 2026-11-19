 
import json
import logging
import os
import sys
 
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi.middleware.cors import CORSMiddleware
 
import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
 
 
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": "devops-api",
            "logger": record.name,
            "message": record.getMessage(),
        }
 
        if hasattr(record, "event"):
            log_data["event"] = record.event
 
        if hasattr(record, "task_id"):
            log_data["task_id"] = record.task_id
 
        if hasattr(record, "method"):
            log_data["method"] = record.method
 
        if hasattr(record, "path"):
            log_data["path"] = record.path
 
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
 
        return json.dumps(log_data)
 
 
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
 
logger = logging.getLogger("devops_demo")
logger.setLevel(logging.INFO)
logger.handlers.clear()
logger.addHandler(handler)
logger.propagate = False
 
 
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
    try:
        with get_db() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    completed BOOLEAN DEFAULT FALSE
                )
            """)
 
        logger.info(
            "Application started and database initialized",
            extra={"event": "application_started"}
        )
 
    except Exception:
        logger.exception(
            "Application startup failed while initializing the database",
            extra={"event": "database_initialization_failed"}
        )
        raise
 
    yield
 
    logger.info(
        "Application shutting down",
        extra={"event": "application_stopped"}
    )
 
 
app = FastAPI(
    title="DevOps Demo API",
    description="Containerized FastAPI and PostgreSQL application",
    version="1.0.0",
    root_path="/api",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
 
        return {
            "database": database,
            "status": "connected"
        }
 
    except Exception:
        logger.exception(
            "Database health check failed. The API could not connect to PostgreSQL",
            extra={"event": "database_health_check_failed"}
        )
        raise HTTPException(
            status_code=500,
            detail="Database health check failed"
        )
 
 
@app.post("/tasks")
def create_task(task: TaskCreate):
    try:
        with get_db() as conn:
            result = conn.execute(
                """
                INSERT INTO tasks (title, description)
                VALUES (%s, %s)
                RETURNING *
                """,
                (task.title, task.description)
            ).fetchone()
 
        logger.info(
            "Task created successfully",
            extra={"event": "task_created"}
        )
 
        return result
 
    except Exception:
        logger.exception(
            "Task creation failed while inserting data into PostgreSQL",
            extra={"event": "task_creation_failed"}
        )
        raise HTTPException(
            status_code=500,
            detail="Unable to create task"
        )
 
 
@app.get("/tasks")
def get_tasks():
    try:
        with get_db() as conn:
            tasks = conn.execute(
                "SELECT * FROM tasks ORDER BY id"
            ).fetchall()
 
        return tasks
 
    except Exception:
        logger.exception(
            "Failed to retrieve tasks from PostgreSQL",
            extra={"event": "task_retrieval_failed"}
        )
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve tasks"
        )
 
 
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    try:
        with get_db() as conn:
            result = conn.execute(
                """
                UPDATE tasks
                SET title = %s, description = %s, completed = %s
                WHERE id = %s
                RETURNING *
                """,
                (
                    task.title,
                    task.description,
                    task.completed,
                    task_id
                )
            ).fetchone()
 
        if result is None:
            logger.warning(
                "Task update failed because the requested task does not exist",
                extra={
                    "event": "task_not_found",
                    "task_id": task_id
                }
            )
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
 
        logger.info(
            "Task updated successfully",
            extra={
                "event": "task_updated",
                "task_id": task_id
            }
        )
 
        return result
 
    except HTTPException:
        raise
 
    except Exception:
        logger.exception(
            "Task update failed due to a database or application error",
            extra={
                "event": "task_update_failed",
                "task_id": task_id
            }
        )
        raise HTTPException(
            status_code=500,
            detail="Unable to update task"
        )
 
 
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    try:
        with get_db() as conn:
            result = conn.execute(
                "DELETE FROM tasks WHERE id = %s RETURNING id",
                (task_id,)
            ).fetchone()
 
        if result is None:
            logger.warning(
                "Task deletion failed because the requested task does not exist",
                extra={
                    "event": "task_not_found",
                    "task_id": task_id
                }
            )
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
 
        logger.info(
            "Task deleted successfully",
            extra={
                "event": "task_deleted",
                "task_id": task_id
            }
        )
 
        return {
            "message": "Task deleted",
            "id": task_id
        }
 
    except HTTPException:
        raise
 
    except Exception:
        logger.exception(
            "Task deletion failed due to a database or application error",
            extra={
                "event": "task_deletion_failed",
                "task_id": task_id
            }
        )
        raise HTTPException(
            status_code=500,
            detail="Unable to delete task"
        )

 