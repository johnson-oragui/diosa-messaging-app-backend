from typing import Any


class RoomNotFoundError(Exception):
    """
    Custom exception class for Room-not-found.
    """
    def __init__(self, message: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(message)

class UserNotAMemberError(RoomNotFoundError):
    """
    Custom error for user not a room member
    """
    pass

class UserNotAnAdminError(RoomNotFoundError):
    """
    Custom error for user not an admin.
    """
    pass

class InvitationNotFoundError(RoomNotFoundError):
    """
    Custom error for invitation not found.
    """
    pass

class CannotDeleteMessageError(RoomNotFoundError):
    """
    Custom error for messages that cannot be deleted.
    """
    pass

class CannotUpdateMessageError(RoomNotFoundError):
    """
    Custom error for messages that cannot be updated.
    """
    pass

class UserDoesNotExistError(RoomNotFoundError):
    """
    Custom error for user not found.
    """
    pass
