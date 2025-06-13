"""
Room DTOs
"""

import json

from typing import Annotated, Optional, List
from pydantic import (
    BaseModel,
    StringConstraints,
    Field,
    HttpUrl,
    ConfigDict,
    model_validator,
)


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


# ++++++++++++++++++++++++++++ Update rooms ++++++++++++++++++++++++++


class UpdateRoomRequestDto(BaseModel):
    """
    UpdateRoomRequestDto
    """

    name: Optional[
        Annotated[
            str, StringConstraints(min_length=2, max_length=50, strip_whitespace=True)
        ]
    ] = Field(default=None, examples=["My Room"])
    room_icon: Optional[HttpUrl] = Field(
        default=None, examples=["https://roomicon.com/image.png"]
    )
    messages_delete_able: Optional[bool] = Field(default=None, examples=[True])
    allow_admin_messages_only: Optional[bool] = Field(default=None, examples=[False])
    is_private: Optional[bool] = Field(default=None, examples=[False])
    room_id: Annotated[
        str, StringConstraints(min_length=20, max_length=40, strip_whitespace=True)
    ] = Field(examples=["22222222222-2222-2222-2222-22222222"])

    @model_validator(mode="before")
    @classmethod
    def validate_fileds(cls, values: dict) -> dict:
        """
        Validates fileds
        """
        if isinstance(values, bytes):
            values = json.loads(values)

        name: str | None = values.get("name", None)
        room_icon: str | None = values.get("room_icon", None)
        messages_delete_able: bool | None = values.get("messages_delete_able", None)
        allow_admin_messages_only: bool | None = values.get(
            "allow_admin_messages_only", None
        )
        is_private: bool | None = values.get("is_private", None)

        if (
            not name
            and not room_icon
            and messages_delete_able is None
            and allow_admin_messages_only is None
            and is_private is None
        ):
            raise ValueError("must provided at least one field for update")

        return values


class UpdateResponseDto(BaseModel):
    """
    Update room response
    """

    message: str = Field(
        default="Room updated successfully.",
        examples=["Room updated successfully."],
    )
    status_code: int = Field(default=201, examples=[200])
    data: dict = Field(default={}, examples=[{}])
