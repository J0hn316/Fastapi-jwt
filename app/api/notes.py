from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.schemas.notes import NoteCreate, NoteOut, NotesListOut, NoteUpdate
from app.services.notes_service import (
    create_note,
    delete_note,
    get_note_for_owner,
    list_notes_for_owner,
    update_note,
)

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note_route(
    payload: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NoteOut:
    note = create_note(db, payload, owner=current_user)
    return note


@router.get("", response_model=NotesListOut)
def list_notes_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    q: str | None = Query(default=None, min_length=1),
) -> NotesListOut:
    items, total = list_notes_for_owner(
        db,
        owner=current_user,
        limit=limit,
        offset=offset,
        q=q,
    )
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get("/{note_id}", response_model=NoteOut)
def get_note_route(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NoteOut:
    note = get_note_for_owner(db, note_id, owner=current_user)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.patch("/{note_id}", response_model=NoteOut)
def update_note_route(
    note_id: int,
    payload: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NoteOut:
    note = get_note_for_owner(db, note_id, owner=current_user)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return update_note(db, note, payload)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note_route(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    note = get_note_for_owner(db, note_id, owner=current_user)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    delete_note(db, note)
    return None
