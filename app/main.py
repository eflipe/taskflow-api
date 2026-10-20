# app/main.py
from fastapi import FastAPI, HTTPException, status
from typing import Optional
from app.schemas import TaskCreate, TaskUpdate, Task

app = FastAPI(title="TaskFlow API", version="1.0.0-mod1")

fake_tasks_db: list[dict] = [
    {"id": 1, "title": "Aprender FastAPI", "completed": False},
    {"id": 2, "title": "Hacer ejercicio", "completed": True},
]


# ---------- Utilidad interna ----------
def _find_task(task_id: int) -> dict:
    """Busca una tarea o lanza 404. Evita duplicar código."""
    for task in fake_tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Tarea con id {task_id} no encontrada",
    )


# ---------- READ (colección) ----------
@app.get("/tasks", response_model=list[Task])
def list_tasks(
    completed: Optional[bool] = None,
    limit: int = 10,
    search: Optional[str] = None,
):
    resultado = fake_tasks_db
    if completed is not None:
        resultado = [t for t in resultado if t["completed"] == completed]
    if search:
        resultado = [t for t in resultado if search.lower() in t["title"].lower()]
    return resultado[:limit]


# ---------- READ (individual) ----------
@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    return _find_task(task_id)


# ---------- CREATE ----------
@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    nueva = {
        "id": max((t["id"] for t in fake_tasks_db), default=0) + 1,
        "title": payload.title,
        "completed": payload.completed,
    }
    fake_tasks_db.append(nueva)
    return nueva


# ---------- UPDATE (parcial) ----------
@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate):
    """
    Actualiza una tarea de forma PARCIAL.
    Solo se actualizan los campos que el cliente envía (no nulos).
    """
    task = _find_task(task_id)

    # payload.model_dump(exclude_unset=True) devuelve solo los campos
    # que el cliente envió explícitamente.
    cambios = payload.model_dump(exclude_unset=True)

    # Aplicamos los cambios sobre el dict de la tarea
    for campo, valor in cambios.items():
        task[campo] = valor

    return task


# ---------- DELETE ----------
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    task = _find_task(task_id)
    fake_tasks_db.remove(task)
    return  # 204 → sin cuerpo