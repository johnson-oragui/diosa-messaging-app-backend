import pytest
from fastapi import status

from app.v1.users.services import user_service

class TestRegisterGoogleRoute:
    """
    Test class for register route.
    """
    @pytest.mark.asyncio
    async def test_register_social_google(self,
                                          client,
                                          mock_google_oauth2):
        """
        Test register social google
        """
        response = client.get("/api/v1/auth/register/social?provider=google")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_register_callback_google(self,
                                            client,
                                            mock_google_oauth2,
                                            mock_google_response,
                                            test_get_session,
                                            test_setup):
        """
        Test register callback for google oauth2
        """
        email = mock_google_response["userinfo"]["email"]
        response = client.get(
            url="/api/v1/auth/callback/google?code=fake_code",
            follow_redirects=False
        )

        assert response.status_code == status.HTTP_302_FOUND

        user = await user_service.fetch({"email": email}, test_get_session)

        assert user.email == email
