from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=100)
    completed: bool = False
    due_date: Optional[datetime] = None
    priority: int = Field(default=1, ge=1, le=5)

    @field_validator("title")
    @classmethod
    def title_no_todo_prefix(cls, v: str) -> str:
        if v.upper().startswith("TODO:"):
            raise ValueError("El título no puede empezar con 'TODO:' (reservado)")
        return v


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(default=None, min_length=1, max_length=100)
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)


class Task(BaseModel):
    id: int
    title: str
    completed: bool
    due_date: Optional[datetime] = None
    priority: int