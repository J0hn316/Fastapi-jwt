from __future__ import annotations

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.db.models import Note, User
from app.schemas.notes import NoteCreate, NoteUpdate


def create_note(db: Session, data: NoteCreate, *, owner: User) -> Note:
    note = Note(title=data.title, content=data.content, owner_id=owner.id)

    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def get_note_for_owner(db: Session, note_id: int, *, owner: User) -> Note | Note:
    stmt = select(Note).where(Note.id == note_id, Note.owner_id == owner.id)
    return db.execute(stmt).scalar_one_or_none()


def list_notes_for_owner(
    db: Session, *, owner: User, limit: int, offset: int, q: str | None = None
) -> tuple[list[Note], int]:
    stmt: Select = select(Note).where(Note.owner_id == owner.id)

    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Note.title.ilike(like), Note.content.ilike(like)))

    total_stmt = select(func.count()).select_from(stmt.subquery())

    stmt = stmt.order_by(Note.updated_at.desc()).limit(limit).offset(offset)

    items = list(db.execute(stmt).scalars().all())
    total = int(db.execute(total_stmt).scalar_one())
    return items, total


def update_note(db: Session, note: Note, data: NoteUpdate) -> Note:
    if data.title is not None:
        note.title = data.title
    if data.content is not None:
        note.content = data.content

    db.commit()
    db.refresh(note)
    return note


def delete_note(db: Session, note: Note) -> None:
    db.delete(note)
    db.commit()
