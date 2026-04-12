from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str | None = None


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = None


class NoteOut(BaseModel):
    id: int
    title: str
    content: str | None
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NotesListOut(BaseModel):
    items: list[NoteOut]
    total: int
    limit: int
    offset: int
