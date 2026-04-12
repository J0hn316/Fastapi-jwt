from fastapi import FastAPI
from sqlalchemy import text

from app.api.auth import router as auth_router
from app.api.notes import router as notes_router
from app.core.config import settings
from app.db.session import engine

app = FastAPI(title=settings.app_name)

app.include_router(auth_router)
app.include_router(notes_router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok"}
