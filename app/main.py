# app/main.py
"""
Punto de entrada de TaskFlow API.

CRUD de tareas en memoria (la base de datos llega en el Módulo 4).
"""

from datetime import datetime

from fastapi import FastAPI, HTTPException, status

from app.schemas import Task, TaskCreate, TaskUpdate


app = FastAPI(
    title="TaskFlow API",
    description="API REST para gestión de tareas personales",
    version="2.0.0-mod2",
)


# ============================================================
# Almacén en memoria (se pierde al reiniciar el servidor)
# ============================================================

fake_tasks_db: list[dict] = [
    {
        "id": 1,
        "title": "Aprender FastAPI",
        "completed": False,
        "priority": 3,
        "description": "Estudiar routers y Pydantic",
        "assignee_email": None,
        "project_url": None,
        "start_date": None,
        "due_date": None,
        "created_at": datetime(2026, 10, 1, 9, 0),
    },
    {
        "id": 2,
        "title": "Hacer ejercicio",
        "completed": True,
        "priority": 2,
        "description": None,
        "assignee_email": "ana@example.com",
        "project_url": None,
        "start_date": None,
        "due_date": None,
        "created_at": datetime(2026, 10, 5, 18, 30),
    },
]


# ============================================================
# Utilidad interna
# ============================================================

def _find_task(task_id: int) -> dict:
    """Busca una tarea por id o lanza 404."""
    for task in fake_tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Tarea con id {task_id} no encontrada",
    )


def _next_id() -> int:
    """Genera el siguiente id disponible (no reutiliza ids borrados)."""
    return max((t["id"] for t in fake_tasks_db), default=0) + 1


# ============================================================
# Endpoints
# ============================================================

@app.get("/")
def read_root():
    """Endpoint raíz: confirma que la API está viva."""
    return {"message": "¡Bienvenido a TaskFlow API!"}


@app.get("/health")
def health_check():
    """Endpoint de salud: útil para monitoreo y despliegue."""
    return {"status": "ok"}


# ---------- READ (colección) ----------
@app.get("/tasks", response_model=list[Task])
def list_tasks(
    completed: bool | None = None,
    limit: int = 10,
    search: str | None = None,
):
    """
    Lista tareas con filtros opcionales:
    - completed: filtra por estado.
    - limit: máximo de resultados (por defecto 10).
    - search: busca texto en el título (case-insensitive).
    """
    resultado = fake_tasks_db

    if completed is not None:
        resultado = [t for t in resultado if t["completed"] == completed]

    if search:
        resultado = [
            t for t in resultado if search.lower() in t["title"].lower()
        ]

    return resultado[:limit]


# ---------- READ (individual) ----------
@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    """Devuelve una tarea por id. 404 si no existe."""
    return _find_task(task_id)


# ---------- CREATE ----------
@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    """
    Crea una nueva tarea.
    El id y created_at los genera el servidor.
    """
    nueva = {
        "id": _next_id(),
        "title": payload.title,
        "completed": payload.completed,
        "priority": payload.priority,
        "description": payload.description,
        "assignee_email": str(payload.assignee_email) if payload.assignee_email else None,
        "project_url": str(payload.project_url) if payload.project_url else None,
        "start_date": payload.start_date,
        "due_date": payload.due_date,
        "created_at": datetime.now(),
    }
    fake_tasks_db.append(nueva)
    return nueva


# ---------- UPDATE (parcial) ----------
@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate):
    """
    Actualiza una tarea de forma PARCIAL.
    Solo se modifican los campos que el cliente envía explícitamente.
    """
    task = _find_task(task_id)

    cambios = payload.model_dump(exclude_unset=True)

    # Convertir EmailStr/HttpUrl a str antes de guardar
    if "assignee_email" in cambios and cambios["assignee_email"] is not None:
        cambios["assignee_email"] = str(cambios["assignee_email"])
    if "project_url" in cambios and cambios["project_url"] is not None:
        cambios["project_url"] = str(cambios["project_url"])

    for campo, valor in cambios.items():
        task[campo] = valor

    return task


# ---------- DELETE ----------
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    """Elimina una tarea por id. 404 si no existe. 204 si se borra."""
    task = _find_task(task_id)
    fake_tasks_db.remove(task)
    return
