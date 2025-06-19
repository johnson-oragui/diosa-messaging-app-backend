"""
Room invitation dto module
"""

from typing import Annotated
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, StringConstraints


class RoomInvitationBaseDto(BaseModel):
    """
    RoomInvitationBaseDto
    """

    id: str = Field(examples=["312423-4-3544354-5-41342165"])
    invitee_id: str = Field(examples=["312423-4-3544354-5-41342165"])
    room_id: str = Field(examples=["312423-4-3544354-5-41342165"])
    invitation_status: str = Field(examples=["pending"])
    expiration: datetime = Field(examples=[datetime.now()])

    model_config = ConfigDict(from_attributes=True)


# +++++++++++++++++++++++++++++++++++++++ ROom invitation request +++++++++++++++++++++++++++===


class RoomInvitationRequestDto(BaseModel):
    """
    RoomInvitationRequestDto
    """

    invitee_id: Annotated[
        str, StringConstraints(min_length=20, max_length=40, strip_whitespace=True)
    ] = Field(examples=["312423-4-3544354-5-41342165"])
    room_id: Annotated[
        str, StringConstraints(min_length=20, max_length=40, strip_whitespace=True)
    ] = Field(examples=["312423-4-3544354-5-41342165"])


class RoomInvitationResponseDto(BaseModel):
    """
    RoomInvitationResponseDto
    """

    status_code: int = Field(default=201, examples=[201])
    message: str = Field(
        default="Invitation sent successfully",
        examples=["Invitation sent successfully"],
    )
    data: RoomInvitationBaseDto


# +++++++++++++++++++++++++++++++++++++++ ROom invitation accept/reject +++++++++++++++++++++++++++===
class InvitationStatusEnum(str, Enum):
    """
    Invitation status enum
    """

    DECLINE = "decline"
    CANCEL = "cancel"
    ACCEPT = "accept"


class RoomInvitationUpdateRequestDto(BaseModel):
    """
    RoomInvitationUpdateRequestDto
    """

    invitation_id: Annotated[
        str, StringConstraints(min_length=20, max_length=40, strip_whitespace=True)
    ] = Field(examples=["312423-4-3544354-5-41342165"])
    room_id: Annotated[
        str, StringConstraints(min_length=20, max_length=40, strip_whitespace=True)
    ] = Field(examples=["312423-4-3544354-5-41342165"])
    action: InvitationStatusEnum = Field(examples=["accept"])


class RoomInvitationUpdateResponseDto(BaseModel):
    """
    RoomInvitationUpdateResponseDto
    """

    status_code: int = Field(default=200, examples=[200])
    message: str = Field(
        default="Invitation request cancelled successfully.",
        examples=["Invitation request cancelled successfully."],
    )
    data: dict = Field(
        examples=[
            {
                "invitation_status": "cancelled",
                "invitation_id": "312423-4-3544354-5-41342165",
            }
        ]
    )


# +++++++++++++++++++++++++++++++++++++++ Fetch ROom invitations +++++++++++++++++++++++++++===
