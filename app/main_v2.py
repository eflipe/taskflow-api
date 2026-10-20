# app/main.py
from fastapi import FastAPI, HTTPException, status
from typing import Optional
from app.schemas import TaskCreate, Task   # 👈 importamos los moldes

app = FastAPI(title="TaskFlow API", version="0.3.0")

fake_tasks_db = [
    {"id": 1, "title": "Aprender FastAPI", "completed": False},
    {"id": 2, "title": "Hacer ejercicio", "completed": True},
]


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    """
    Crea una nueva tarea.
    - `payload` es el cuerpo (body) de la petición, ya validado por Pydantic.
    """
    nueva = {
        "id": len(fake_tasks_db) + 1,
        "title": payload.title,
        "completed": payload.completed,
    }
    fake_tasks_db.append(nueva)
    return nueva