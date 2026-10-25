from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path
from datetime import timedelta

import pytest
from jose import jwt
from fastapi import HTTPException

from app.core.config import settings
from app.core.security import create_access_token, decode_access_token


def run_config_check(
    tmp_path: Path,
    *,
    secret: str | None,
) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]

    # Copy the environment without any existing JWT signing key.
    env = {
        key: value
        for key, value in os.environ.items()
        if key.upper() != "JWT_SECRET_KEY"
    }

    env["PYTHONPATH"] = os.pathsep.join([str(project_root), env.get("PYTHONPATH", "")])

    if secret is not None:
        env["JWT_SECRET_KEY"] = secret

    return subprocess.run(
        [
            sys.executable,
            "-c",
            "from app.core.config import settings; print('loaded')",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )


def test_missing_jwt_secret_prevents_startup(tmp_path: Path) -> None:
    result = run_config_check(tmp_path, secret=None)

    assert result.returncode != 0
    assert "jwt_secret_key" in result.stderr.lower()


def test_jwt_secret_can_load_from_environment(tmp_path: Path) -> None:
    result = run_config_check(
        tmp_path,
        secret="test-only-secret-not-for-deployment",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "loaded"


def test_access_token_round_trip(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        settings,
        "jwt_secret_key",
        "test-only-signing-secret",
    )

    token = create_access_token(subject="123")
    payload = decode_access_token(token)

    assert payload["sub"] == "123"
    assert "exp" in payload


def test_token_signed_with_wrong_secret_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "jwt_secret_key",
        "correct-test-only-secret",
    )

    forged_token = jwt.encode(
        {"sub": "123"},
        "incorrect-test-only-secret",
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(forged_token)

    assert exc_info.value.status_code == 401


def test_expired_access_token_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "jwt_secret_key",
        "test-only-signing-secret",
    )

    token = create_access_token(
        subject="123",
        expires_delta=timedelta(seconds=-10),
    )

    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(token)

    assert exc_info.value.status_code == 401
