import pytest
from unittest.mock import patch
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_get_current_user(client: AsyncClient, user_token: str):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await client.get("/users/me", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert "email" in data
    assert "username" in data


@patch("src.routes.users.UploadFileService.upload_file")
async def test_update_avatar(mock_upload, client: AsyncClient, user_token: str):
    headers = {"Authorization": f"Bearer {user_token}"}
    mock_upload.return_value = "http://example.com/fake_avatar.png"

    file_path = "tests/test_avatar.png"
    with open(file_path, "rb") as f:
        files = {"file": ("test_avatar.png", f, "image/png")}
        response = await client.patch("/users/avatar", headers=headers, files=files)

    assert response.status_code == 200
    data = response.json()
    assert "avatar" in data
    assert data["avatar"] == "http://example.com/fake_avatar.png"
