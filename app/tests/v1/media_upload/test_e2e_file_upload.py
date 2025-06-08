"""
Test File upload message module
"""

from unittest.mock import patch
import io
import pytest
from httpx import AsyncClient

from app.tests.v1.direct_message import register_input


class TestFileMediaUpload:
    """
    Test File Media upload route
    """

    @pytest.mark.asyncio
    async def test_a_user_can_upload_File_successfully(
        self, test_setup: None, client: AsyncClient
    ):
        """
        Tests user can upload File successfully
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00000sddeee0-00d0-0000-0000-00qde0001",
        }

        with patch(
            "app.service.v1.authentication_service.AuthenticationService.send_email",
            return_value=None,
        ):
            with patch(
                "app.service.v1.authentication_service.AuthenticationService.generate_six_digit_code",
                return_value="123456",
            ):
                with patch(
                    "app.service.v1.media_upload_service.MediaUploadService.upload_to_cloudinary",
                    return_value="https://cloudinary.com/fake.pdf",
                ):
                    # register first user
                    response0 = await client.post(
                        url="/api/v1/auth/register", json=register_input
                    )
                    assert response0.status_code == 201

                    # verify first user
                    await client.patch(
                        url="/api/v1/auth/verify-account",
                        json={"email": register_input.get("email"), "code": "123456"},
                    )

                    # login first user
                    response1 = await client.post(
                        url="/api/v1/auth/login", json=login_payload
                    )

                    assert response1.status_code == 200

                    data1: dict = response1.json()

                    access_token = data1["data"]["access_token"]["token"]

                    image_content = b"Image file content"
                    image_file = io.BytesIO(image_content)

                    response2 = await client.post(
                        url="/api/v1/media-uploads/files",
                        headers={"Authorization": f"Bearer {access_token}"},
                        files=[
                            (
                                ("media_to_upload"),
                                ("photo1.png", image_file, "application/json"),
                            )
                        ],
                    )

                    assert response2.status_code == 201
                    data2: dict = response2.json()

                    assert data2["message"] == "media uploaded successfully"
                    assert (
                        data2["data"]["media_url"] == "https://cloudinary.com/fake.pdf"
                    )
                    assert data2["data"]["media_type"] == "file"

    @pytest.mark.asyncio
    async def test_b_when_invalid_content_type_returns_400(
        self, test_setup: None, client: AsyncClient
    ):
        """
        Tests when invalid content type returns 400
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00000sddeee0-0000-0000-sas0-ss000sa1",
        }

        with patch(
            "app.service.v1.authentication_service.AuthenticationService.send_email",
            return_value=None,
        ):
            with patch(
                "app.service.v1.authentication_service.AuthenticationService.generate_six_digit_code",
                return_value="123456",
            ):
                with patch(
                    "app.service.v1.media_upload_service.MediaUploadService.upload_to_cloudinary",
                    return_value="https://cloudinary.com/fake.pdf",
                ):
                    # register first user
                    response0 = await client.post(
                        url="/api/v1/auth/register", json=register_input
                    )
                    assert response0.status_code == 201

                    # verify first user
                    await client.patch(
                        url="/api/v1/auth/verify-account",
                        json={"email": register_input.get("email"), "code": "123456"},
                    )

                    # login first user
                    response1 = await client.post(
                        url="/api/v1/auth/login", json=login_payload
                    )

                    assert response1.status_code == 200

                    data1: dict = response1.json()

                    access_token = data1["data"]["access_token"]["token"]

                    image_content = b"Image file content"
                    image_file = io.BytesIO(image_content)

                    response2 = await client.post(
                        url="/api/v1/media-uploads/files",
                        headers={"Authorization": f"Bearer {access_token}"},
                        files=[
                            (
                                ("media_to_upload"),
                                ("photo1.png", image_file, "application/none"),
                            )
                        ],
                    )

                    assert response2.status_code == 400
                    data2: dict = response2.json()

                    assert data2["message"].startswith(
                        "Unsupported content_type. content_type must be one of"
                    )

    @pytest.mark.asyncio
    async def test_c_when_file_size_too_large_returns_400(
        self, test_setup: None, client: AsyncClient
    ):
        """
        Tests when file size too large returns 400
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00000sddeee0-0000-wwww-0000-sssw0031",
        }

        with patch(
            "app.service.v1.authentication_service.AuthenticationService.send_email",
            return_value=None,
        ):
            with patch(
                "app.service.v1.authentication_service.AuthenticationService.generate_six_digit_code",
                return_value="123456",
            ):
                with patch(
                    "app.service.v1.media_upload_service.MediaUploadService.upload_to_cloudinary",
                    return_value="https://cloudinary.com/fake.json",
                ):
                    # register first user
                    response0 = await client.post(
                        url="/api/v1/auth/register", json=register_input
                    )
                    assert response0.status_code == 201

                    # verify first user
                    await client.patch(
                        url="/api/v1/auth/verify-account",
                        json={"email": register_input.get("email"), "code": "123456"},
                    )

                    # login first user
                    response1 = await client.post(
                        url="/api/v1/auth/login", json=login_payload
                    )

                    assert response1.status_code == 200

                    data1: dict = response1.json()

                    access_token = data1["data"]["access_token"]["token"]

                    image_content = b"Image file content" * (2 * 1024 * 1024)
                    image_file = io.BytesIO(image_content)

                    response2 = await client.post(
                        url="/api/v1/media-uploads/files",
                        headers={"Authorization": f"Bearer {access_token}"},
                        files=[
                            (
                                ("media_to_upload"),
                                ("photo1.png", image_file, "application/json"),
                            )
                        ],
                    )

                    assert response2.status_code == 400
                    data2: dict = response2.json()

                    assert data2["message"].startswith(
                        "FIle size exceeds the limit of 1MB"
                    )
