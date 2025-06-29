"""
DirectMEssage DTO
"""

from datetime import datetime, timezone
import json
from typing import Annotated, List, Optional
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl, StringConstraints, model_validator
from bleach import clean


class RoomMessageBaseDto(BaseModel):
    """
    Message base schema
    """

    id: str = Field(examples=["123124-1242-5435-5645765"])
    sender_id: str = Field(examples=["342442-1242-5435-5645765"])
    room_id: str = Field(examples=["123124-1242-99999-5645765"])
    parent_message_id: Optional[str] = Field(
        default=None, examples=["123124-1242-5435-1111111"]
    )
    status: str = Field(examples=["sent"])

    is_edited: bool = Field(examples=[False])
    created_at: datetime = Field(examples=[datetime.now(timezone.utc)])
    content: Optional[str] = Field(default=None, examples=["Hello"])
    media_url: Optional[str] = Field(
        default=None, examples=["https://media_url.com/image"]
    )
    media_type: Optional[str] = Field(default=None, examples=["image"])


# +++++++++++++++++++++++++++++++++++++++ send message +++++++++++++++++++++++++++++++++++++++++


class SendRoomMessageRequestDto(BaseModel):
    """
    Send Message schema
    """

    message: Optional[
        Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
    ] = Field(examples=["Hello"], default=None)
    media_url: Optional[HttpUrl] = Field(
        default=None, examples=["https://media_url.com/image"]
    )
    media_type: Optional[str] = Field(default=None, examples=["image"])
    parent_message_id: Optional[
        Annotated[str, StringConstraints(min_length=10, strip_whitespace=True)]
    ] = Field(default=None, examples=["143423-2342353-5345-364645"])
    room_id: Annotated[str, StringConstraints(min_length=10, strip_whitespace=True)] = (
        Field(examples=["234123-423423-5454-6455"])
    )

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values: dict) -> dict:
        """
        Validates fields
        """
        if isinstance(values, bytes):
            values = json.loads(values)
        message: str | None = values.get("message", None)
        media_type: str | None = values.get("media_type", None)
        media_url: str | None = values.get("media_url", None)

        if media_type:
            if media_type not in ["image", "video", "text", "audio", "file"]:
                raise ValueError("mdeia_type must only be video, image, or text")

        if media_url and not media_type:
            raise ValueError("media_type must be provided when media_url is provided")
        if media_url and media_type not in ["image", "video", "audio", "file"]:
            raise ValueError(
                f"media_type must not be {media_type} when media_url is provided"
            )
        if not media_type:
            values["media_type"] = "text"
        if not message and not media_url:
            raise ValueError("Message must have content or media.")

        if message:
            values["message"] = clean(message)

        return values


class SendRoomMessageResponseDto(BaseModel):
    """
    Send message response
    """

    message: str = Field(
        default="message sent successfully", examples=["message sent successfully"]
    )
    status_code: int = Field(default=201, examples=[201])
    data: RoomMessageBaseDto


# +++++++++++++++++++++++++++++++++++++++ all messages +++++++++++++++++++++++++++++++++++++++++
# All messages
class AllRoomMessagesResponseDto(BaseModel):
    """
    All  messages schema
    """

    message: str = Field(
        default="messages retrieved successfully",
        examples=["messages retrieved successfully"],
    )
    status_code: int = Field(default=200, examples=[200])
    page: int = Field(default=1, examples=[1])
    limit: int = Field(default=20, examples=[20])
    total_pages: int = Field(examples=[10])
    total_messages: int = Field(examples=[100])

    data: List[Optional[RoomMessageBaseDto]]


class RoomMessageOrderEnum(str, Enum):
    """
    Room message order by enum
    """

    DESC = "desc"
    ASC = "asc"
