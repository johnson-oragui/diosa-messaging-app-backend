from typing import Annotated, Optional, List
from uuid import uuid4
from datetime import datetime, timezone
from pydantic import (
    BaseModel,
    Field,
    StringConstraints,
    ConfigDict,
    model_validator,
    HttpUrl
)
from unicodedata import normalize
from bleach import clean

class RoomCreateSchema(BaseModel):
    """
    Model class for room creation
    """
    room_name: Annotated[
        Optional[str],
        StringConstraints(
            strip_whitespace=True,
            max_length=30
        )
    ] = Field(
        examples=["sweet room"]
    )
    room_type: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            max_length=30,
            min_length=3
        )
    ] = Field(
        examples=["private"]
    )

    description: Annotated[
        Optional[str],
        StringConstraints(
            strip_whitespace=True,
            max_length=60
        )
    ] = Field(
        default="",
        examples=["New Room"]
    )

    messages_deletable: bool = Field(
        examples=[True]
    )

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values: dict) -> dict:
        """
        Validate fields.
        """
        room_type: str | None = values.get("room_type")
        room_name: str | None = values.get("room_name")
        messages_deletable: bool | None = values.get("messages_deletable")

        # validate room_type
        if room_type != "private" and room_type != "public":
            raise ValueError("room_type must be either public or private")

        # validate messages_deletable
        if not isinstance(messages_deletable, bool) or not messages_deletable:
            raise ValueError("messages_deletable must be either true of false")

        # validate room_name
        if not room_name:
            raise ValueError("room_name cannot bu null")
        notallowed_characters = "!`~@$%^&*()+\"=// \\<>?|"
        if any(char for char in room_name if char in notallowed_characters):
            raise ValueError("Only special characters #-_ are allowed in room_name")

        values["room_name"] = normalize("NFKC", clean(room_name))
        values["room_type"] = normalize("NFKC", clean(room_type))
        return values

class CreateDirectMessageSchema(BaseModel):
    """
    Class for direct message creation
    """
    receiver_id: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True
        )
    ]

    @model_validator(mode="before")
    @classmethod
    def validate_fiels(cls, values: dict) -> dict:
        """
        Validates fields
        """
        receiver_id: str | None = values.get("receiver_id")
        notallowed_chars = " !@$%^&*()+= <>,.?/\\"

        if any(char for char in receiver_id if char in notallowed_chars):
            raise ValueError("Invalid receiver_id")
        if not receiver_id:
            raise ValueError("receiver_id cannot be null")

        values["receiver_id"] = normalize("NFKC", clean(receiver_id))

        return values

class RoomBase(BaseModel):
    """
    Base class for room.
    """
    id: str = Field(examples=["66fff849-aa58-800a-b32d-6efabc1bcee2"])
    creator_id: str = Field(examples=["66fff849-aa58-800a-b32d-6efabc1basas"])
    room_name: str = Field(examples=["Great room"])
    room_type: str = Field(examples=["private"])
    description: Optional[str] = Field(examples=["Good room for friends"])
    messages_deletable: bool = Field(examples=[False])
    created_at: datetime = Field(examples=[datetime.now(timezone.utc)])
    updated_at: datetime = Field(examples=[datetime.now(timezone.utc)])

    model_config = ConfigDict(from_attributes=True)

class RoomMembersBase(BaseModel):
    """
    Class fior room members base.
    """
    id: str  = Field(examples=["aa987f849-aa58-800a-b32d-6efabc1baazz"])
    user_id: str = Field(examples=["66fff849-aa58-800a-b32d-6efabc1bcee2"])
    room_id: str = Field(examples=["66fff849-aa58-800a-b32d-6efabc1baazz"])
    invited_at: datetime = Field(examples=[datetime.now(timezone.utc)])
    room_type: str = Field(examples=["private"])
    is_admin: bool = Field(examples=[True])
    created_at: datetime = Field(examples=[datetime.now(timezone.utc)])
    updated_at: datetime = Field(examples=[datetime.now(timezone.utc)])

    model_config = ConfigDict(from_attributes=True)

class RoomAndRoomMembersBase(BaseModel):
    """
    Class for room and room members data.
    """
    room: RoomBase
    room_members: List[RoomMembersBase]

class RoomSchemaOut(BaseModel):
    """
    Class for room response.
    """
    status_code: int = Field(examples=[201])
    message: str = Field(examples=["Successful"])
    data: RoomAndRoomMembersBase

class RoomBelongsToResponse(BaseModel):
    """
    Class for rooms user belongs to response.
    """
    status_code: int = Field(default=200, examples=[200])
    message: str = Field(default="Rooms Retrieved Successfully", examples=["Rooms Retrieved Successfully"])
    data: List[Optional[RoomBase]]

class DMBase(BaseModel):
    """
    Class for DM retrieval.
    """
    room_id: str
    room_name: str
    user_id: str
    avatar_url: Optional[HttpUrl]
    username: str

class AllDirectRoomsResponse(RoomBelongsToResponse):
    """
    Schema for direct message GET response.
    """
    data: List[Optional[DMBase]]

__all__ = [
    "RoomCreateSchema", "RoomSchemaOut", "RoomAndRoomMembersBase", "RoomBase",
    "RoomMembersBase", "CreateDirectMessageSchema", "RoomBelongsToResponse",
    "AllDirectRoomsResponse",
]
