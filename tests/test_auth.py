from __future__ import annotations

from fastapi.testclient import TestClient


def test_register_user_success(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={"email": "user1@example.com", "password": "supersecret123"},
    )

    assert response.status_code == 201

    data = response.json()
    assert data["email"] == "user1@example.com"
    assert "id" in data
    assert "created_at" in data
    assert "hashed_password" not in data


def test_register_duplicate_email_fails(client: TestClient) -> None:
    payload = {
        "email": "duplicate@example.com",
        "password": "supersecret123",
    }

    first = client.post("/auth/register", json=payload)
    second = client.post("/auth/register", json=payload)

    assert first.status_code == 201
    assert second.status_code == 400
    assert second.json()["detail"] == "Email is already registered."


def test_login_success_returns_token(client: TestClient) -> None:
    client.post(
        "/auth/register",
        json={
            "email": "login@example.com",
            "password": "supersecret123",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "supersecret123",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password_fails(client: TestClient) -> None:
    client.post(
        "/auth/register",
        json={
            "email": "wrongpass@example.com",
            "password": "supersecret123",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "nottherightpassword",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_notes_requires_auth(client: TestClient) -> None:
    response = client.get("/notes")
    assert response.status_code == 401
