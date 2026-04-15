from __future__ import annotations

from fastapi.testclient import TestClient


def register_and_login(client: TestClient, email: str, password: str) -> str:
    register_response = client.post(
        "/auth/register", json={"email": email, "password": password}
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login", json={"email": email, "password": password}
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_user_can_create_and_list_only_their_own_notes(client: TestClient) -> None:
    token_1 = register_and_login(client, "owner1@example.com", "supersecret123")
    token_2 = register_and_login(client, "owner2@example.com", "supersecret123")

    create_response = client.post(
        "/notes",
        headers=auth_headers(token_1),
        json={
            "title": "Owner 1 Note",
            "content": "Belongs to user 1",
        },
    )
    assert create_response.status_code == 201

    notes_user_1 = client.get("/notes", headers=auth_headers(token_1))
    assert notes_user_1.status_code == 200
    data_1 = notes_user_1.json()
    assert data_1["total"] >= 1
    titles_1 = [item["title"] for item in data_1["items"]]
    assert "Owner 1 Note" in titles_1

    notes_user_2 = client.get("/notes", headers=auth_headers(token_2))
    assert notes_user_2.status_code == 200
    data_2 = notes_user_2.json()
    titles_2 = [item["title"] for item in data_2["items"]]
    assert "Owner 1 Note" not in titles_2


def test_user_cannot_get_another_users_note(client: TestClient) -> None:
    token_1 = register_and_login(client, "get1@example.com", "supersecret123")
    token_2 = register_and_login(client, "get2@example.com", "supersecret123")

    create_response = client.post(
        "/notes",
        headers=auth_headers(token_1),
        json={
            "title": "Private Note",
            "content": "Only owner should access this",
        },
    )
    assert create_response.status_code == 201
    note_id = create_response.json()["id"]

    response = client.get(f"/notes/{note_id}", headers=auth_headers(token_2))
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_user_cannot_update_another_users_note(client: TestClient) -> None:
    token_1 = register_and_login(client, "update1@example.com", "supersecret123")
    token_2 = register_and_login(client, "update2@example.com", "supersecret123")

    create_response = client.post(
        "/notes",
        headers=auth_headers(token_1),
        json={
            "title": "Original Title",
            "content": "Original content",
        },
    )
    assert create_response.status_code == 201
    note_id = create_response.json()["id"]

    update_response = client.patch(
        f"/notes/{note_id}",
        headers=auth_headers(token_2),
        json={
            "title": "Hacked Title",
        },
    )

    assert update_response.status_code == 404
    assert update_response.json()["detail"] == "Note not found"


def test_user_cannot_delete_another_users_note(client: TestClient) -> None:
    token_1 = register_and_login(client, "delete1@example.com", "supersecret123")
    token_2 = register_and_login(client, "delete2@example.com", "supersecret123")

    create_response = client.post(
        "/notes",
        headers=auth_headers(token_1),
        json={
            "title": "Delete Protected",
            "content": "Should not be deletable by another user",
        },
    )
    assert create_response.status_code == 201
    note_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/notes/{note_id}",
        headers=auth_headers(token_2),
    )

    assert delete_response.status_code == 404
    assert delete_response.json()["detail"] == "Note not found"
