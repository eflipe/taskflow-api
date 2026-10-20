# app/main.py
from typing import Optional

from fastapi import FastAPI, HTTPException, status

app = FastAPI(
    title="TaskFlow API",
    description="API REST para gestión de tareas personales",
    version="0.2.0",
)

# Almacén temporal en memoria (¡se borra al reiniciar el servidor!)
# En el Módulo 4 lo cambiaremos por una base de datos real.
fake_tasks_db = [
    {"id": 1, "title": "Aprender FastAPI", "completed": False},
    {"id": 2, "title": "Hacer ejercicio", "completed": True},
]


@app.get("/")
def read_root():
    return {"message": "¡Bienvenido a TaskFlow API!"}


# GET: leer todas las tareas
@app.get("/tasks")
def list_tasks(
    completed: Optional[bool] = None,   # opcional  
    limit: int = 10,                    # valor por defecto 10
    search: Optional[str] = None,       # buscar por texto en el título
    order_by: str = "id"                 # ordenar por "id" o "title", por defecto "id"
):
    """
    Lista tareas con filtros opcionales.
    - completed: filtra por estado (true/false). Si no se envía, no filtra.
    - limit: máximo de resultados (por defecto 10).
    - search: texto a buscar dentro del título.
    - order_by: campo por el cual ordenar (por defecto "id").
    """
    resultado = fake_tasks_db

    # Filtro por estado
    if completed is not None:
        resultado = [t for t in resultado if t["completed"] == completed]

    # Filtro por texto (case-insensitive)
    if search:
        resultado = [t for t in resultado if search.lower() in t["title"].lower()]

    # Ordenar resultados
    if order_by == "title":
        resultado = sorted(resultado, key=lambda x: x["title"])

    # Limitar resultados
    return resultado[:limit]

# Añade un query param order_by que acepte "id" o "title" y ordene la lista. Valor por defecto: "id"

# GET: contar todas las tareas
@app.get("/tasks/count")
def get_tasks_count():
    """Devuelve el número total de tareas."""
    return {"count": len(fake_tasks_db)}

# GET una tarea concreta por su ID
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    """
    Devuelve una tarea por su ID.
    - Si existe: la devuelve.
    - Si no existe: error 404.
    """
    for task in fake_tasks_db:
        if task["id"] == task_id:
            return task

    # Si llegamos aquí, no existe → lanzamos un 404
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Tarea con id {task_id} no encontrada",
    )

# PUT marca completa una tarea concreta por su ID
@app.put("/tasks/{task_id}/complete")
def put_task(task_id: int):
    """
    Marca una tarea como completada por su ID.
    - Si existe: la devuelve.
    - Si no existe: error 404.
    """
    for task in fake_tasks_db:
        if task["id"] == task_id:
            task["completed"] = True
            return task

    # Si llegamos aquí, no existe → lanzamos un 404
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Tarea con id {task_id} no encontrada",
    )

# DELETE: borra todas las tareas
@app.delete("/tasks/all")
def delete_tasks():
    """Borra todas las tareas."""
    fake_tasks_db.clear()
    return {"message": "Todas las tareas han sido eliminadas."}

# DELETE una tarea concreta por su ID
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    """
    Elimina una tarea por su ID.
    - Si existe: la elimina y devuelve.
    - Si no existe: error 404.
    """
    for task in fake_tasks_db:
        if task["id"] == task_id:
            fake_tasks_db.remove(task)
            return {"message": f"Tarea con id {task_id} ha sido eliminada."}

    # Si llegamos aquí, no existe → lanzamos un 404
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Tarea con id {task_id} no encontrada",
    )



# POST: crear una tarea nueva (por ahora sin validación, la añadimos en 1.3)
@app.post("/tasks")
def create_task():
    """Crea una tarea de ejemplo (versión tonta por ahora)."""
    nueva = {"id": len(fake_tasks_db) + 1, "title": "A - Tarea de ejemplo", "completed": False}
    fake_tasks_db.append(nueva)
    return nueva