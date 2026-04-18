# FastAPI JWT Notes

A production-style backend API built with FastAPI, SQLite, SQLAlchemy, and JWT authentication.

## Features
- User registration and login
- Password hashing
- JWT authentication
- Ownership-based authorization
- SQLite + Alembic migrations
- Automated tests with Pytest

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python run.py
```

## API Docs
http://127.0.0.1:8000/docs

## Auth Flow

### Register
POST /auth/register

### Login
POST /auth/login

Returns JWT token.

### Use Token
Authorization: Bearer <token>

## Run Tests
```bash
pytest -v
```
