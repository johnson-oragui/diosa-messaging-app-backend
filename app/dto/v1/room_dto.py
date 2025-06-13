"""
Room DTOs
"""

from typing import Annotated, Optional, List
from pydantic import BaseModel, StringConstraints, Field, HttpUrl, ConfigDict


class RoomBaseDto(BaseModel):
    """
    RoomBase DTO
    """

    id: str = Field(examples=["111111111111-1111-s222-w22w2344"])
    owner_id: str = Field(examples=["My Room"])
    name: str = Field(examples=["My Room"])
    room_icon: Optional[str] = Field(
        default=None, examples=["https://roomicon.com/image.png"]
    )
    messages_delete_able: bool = Field(examples=[True])
    is_deactivated: bool = Field(examples=[False])
    allow_admin_messages_only: bool = Field(examples=[False])
    is_private: bool = Field(examples=[False])

    model_config = ConfigDict(from_attributes=True)


# ++++++++++++++++++++++++ CREATE ROOM ++++++++++++++++++++++++++++++++++


class CreateRoomRequestDto(BaseModel):
    """
    CreateRoomRequestDto
    """

    name: Annotated[
        str, StringConstraints(min_length=2, max_length=50, strip_whitespace=True)
    ] = Field(examples=["My Room"])
    room_icon: Optional[HttpUrl] = Field(
        default=None, examples=["https://roomicon.com/image.png"]
    )
    messages_delete_able: bool = Field(examples=[True])
    is_deactivated: bool = Field(examples=[False])
    allow_admin_messages_only: bool = Field(examples=[False])
    is_private: bool = Field(examples=[False])


class CreateRoomResponseDto(BaseModel):
    """
    CreateRoomResponseDto
    """

    message: str = Field(
        default="Room created successfully.", examples=["Room created successfully."]
    )
    status_code: int = Field(default=201, examples=[201])
    data: RoomBaseDto


# ++++++++++++++++++++++++++++ Retrieve rooms ++++++++++++++++++++++++++
class RetrieveResponseDto(BaseModel):
    """
    Retrieve room
    """

    message: str = Field(
        default="Rooms retrieved successfully.",
        examples=["Rooms retrieved successfully."],
    )
    status_code: int = Field(default=201, examples=[200])
    page: int = Field(examples=[1])
    limit: int = Field(examples=[10])
    total_pages: int = Field(examples=[1])
    total_rooms: int = Field(examples=[10])
    data: List[Optional[RoomBaseDto]]
