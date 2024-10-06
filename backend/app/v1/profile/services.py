from app.base.services import Service
from app.v1.profile import Profile

class ProfileService(Service):
    """
    Service class for user's profile
    """
    def __init__(self) -> None:
        """
        Constructor
        """
        super().__init__(Profile)

profile_service = ProfileService()
