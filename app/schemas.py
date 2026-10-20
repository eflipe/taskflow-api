# app/schemas.py
"""
Modelos Pydantic de TaskFlow API.

Contiene los esquemas de entrada (TaskCreate, TaskUpdate) y de salida (Task),
junto con tipos reutilizables y validadores.
"""

from datetime import datetime
from typing import Optional, Annotated

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    EmailStr,
    HttpUrl,
    field_validator,
    model_validator,
    field_serializer,
)


# ============================================================
# Tipos reutilizables con validaciones (Annotated + Field)
# ============================================================

TaskTitle = Annotated[
    str,
    Field(
        min_length=1,
        max_length=100,
        description="Título de la tarea (1 a 100 caracteres)",
    ),
]

TaskPriority = Annotated[
    int,
    Field(ge=1, le=5, description="Prioridad de 1 (baja) a 5 (alta)"),
]

TaskDescription = Annotated[
    str,
    Field(max_length=500, description="Descripción opcional de hasta 500 caracteres"),
]


# ============================================================
# Modelo base: campos compartidos
# ============================================================

class TaskBase(BaseModel):
    """
    Campos y validaciones compartidos por todos los modelos de tarea.
    No se instancia directamente: es la clase base.
    """

    model_config = ConfigDict(extra="forbid")

    title: TaskTitle
    completed: bool = False
    priority: TaskPriority = 1
    description: Optional[TaskDescription] = None
    assignee_email: Optional[EmailStr] = None
    project_url: Optional[HttpUrl] = None

    @field_validator("title")
    @classmethod
    def title_no_todo_prefix(cls, v: str) -> str:
        """Rechaza títulos que empiecen con 'TODO:' (prefijo reservado)."""
        if v.upper().startswith("TODO:"):
            raise ValueError("El título no puede empezar con 'TODO:' (reservado)")
        return v


# ============================================================
# Modelo de entrada: POST /tasks
# ============================================================

class TaskCreate(TaskBase):
    """
    Entrada para crear una tarea.
    Hereda todos los campos y validadores de TaskBase y añade los campos
    específicos de la creación (fechas planificadas).
    """

    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None

    @model_validator(mode="after")
    def validate_dates(self):
        """
        Reglas cruzadas sobre fechas:
        - due_date no puede ser una fecha pasada.
        - Si existen start_date y due_date, due_date debe ser posterior.
        """
        ahora = datetime.now()

        if self.due_date is not None and self.due_date < ahora:
            raise ValueError("due_date no puede ser una fecha pasada")

        if (
            self.start_date is not None
            and self.due_date is not None
            and self.due_date <= self.start_date
        ):
            raise ValueError("due_date debe ser posterior a start_date")

        return self


# ============================================================
# Modelo de entrada: PATCH /tasks/{id}
# ============================================================

class TaskUpdate(BaseModel):
    """
    Entrada para actualización parcial.
    NO hereda de TaskBase porque todos los campos deben ser opcionales:
    el cliente envía solo lo que quiere cambiar.
    """

    model_config = ConfigDict(extra="forbid")

    title: Optional[TaskTitle] = None
    completed: Optional[bool] = None
    priority: Optional[TaskPriority] = None
    description: Optional[TaskDescription] = None
    assignee_email: Optional[EmailStr] = None
    project_url: Optional[HttpUrl] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None


# ============================================================
# Modelo de salida: respuestas
# ============================================================

class Task(TaskBase):
    """
    Representación de una tarea devuelta al cliente.
    Hereda TaskBase y añade los campos generados por el servidor.
    """

    id: int
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    created_at: datetime

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        """Devuelve created_at en formato 'YYYY-MM-DD HH:MM' en la respuesta."""
        return value.strftime("%Y-%m-%d %H:%M")
