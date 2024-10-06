import pytest
from fastapi import status

from app.v1.users.services import user_service

class TestRegisterGithubRoute:
    """
    Test class for register route.
    """
    @pytest.mark.asyncio
    async def test_register_social_github(self,
                                          client,
                                          mock_github_oauth2):
        """
        Test register social github
        """
        response = client.get("/api/v1/auth/register/social?provider=github")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_register_callback_github(self,
                                            client,
                                            mock_github_oauth2,
                                            mock_github_response,
                                            test_get_session,
                                            test_setup):
        """
        Test register callback for github oauth2
        """
        email = mock_github_response["userinfo"]["email"]

        response = client.get(
            url=f"/api/v1/auth/callback/github?code=fake-code",
            follow_redirects=False
        )

        assert response.status_code == status.HTTP_302_FOUND

        user = await user_service.fetch({"email": email}, test_get_session)

        assert user.email == email
