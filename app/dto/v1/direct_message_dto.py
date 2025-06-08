"""
DirectMEssage DTO
"""

from datetime import datetime, timezone
import json
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field, HttpUrl, StringConstraints, model_validator
from bleach import clean


class MessageBaseDto(BaseModel):
    """
    Message base schema
    """

    id: str = Field(examples=["123124-1242-5435-5645765"])
    sender_id: str = Field(examples=["342442-1242-5435-5645765"])
    recipient_id: str = Field(examples=["123124-1242-99999-5645765"])
    conversation_id: str = Field(examples=["111111-1242-99999-5645765"])
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


class SendMessageDto(BaseModel):
    """
    Send Message schema
    """

    message: Optional[
        Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
    ] = Field(examples=["Hello"], default=None)
    conversation_id: Optional[
        Annotated[str, StringConstraints(min_length=10, strip_whitespace=True)]
    ] = Field(default=None, examples=["13124-234354-4534-5346464"])
    media_url: Optional[HttpUrl] = Field(
        default=None, examples=["https://media_url.com/image"]
    )
    media_type: Optional[str] = Field(default=None, examples=["image"])
    parent_message_id: Optional[
        Annotated[str, StringConstraints(min_length=10, strip_whitespace=True)]
    ] = Field(default=None, examples=["143423-2342353-5345-364645"])
    recipient_id: Annotated[
        str, StringConstraints(min_length=10, strip_whitespace=True)
    ] = Field(examples=["234123-423423-5454-6455"])

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


class SendMessageResponseDto(BaseModel):
    """
    Send message response
    """

    message: str = Field(
        default="message sent successfully", examples=["message sent successfully"]
    )
    status_code: int = Field(default=201, examples=[201])
    data: MessageBaseDto


# +++++++++++++++++++++++++++++++++++++++ all messages +++++++++++++++++++++++++++++++++++++++++
# All messages
class AllMessagesResponseDto(BaseModel):
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

    data: List[Optional[MessageBaseDto]]


# +++++++++++++++++++++++++++++++++++++++ delete message +++++++++++++++++++++++++++++++++++++++++


# delete message response


class DeleteMessageDto(BaseModel):
    """
    Schema for message delete
    """

    message_ids: List[str] = Field(
        examples=[["12312432-42345435-4564645", "1234324-23453-53454-645"]]
    )
    delete_for_both: bool = Field(default=False, examples=[False])

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values: dict) -> dict:
        """
        Validates fields
        """
        if isinstance(values, bytes):
            values = json.loads(values)

        message_ids = values.get("message_ids", [])

        if not isinstance(message_ids, list):
            raise ValueError("message_ids must be of type list/array")
        validated_message_ids = []
        for id_ in message_ids:
            validated_message_ids.append(clean(id_))

        values["message_ids"] = validated_message_ids
        return values


class DeleteMessageResponseDto(BaseModel):
    """
    Delete message schema
    """

    message: str = Field(
        default="message(s) deleted successfully",
        examples=["message(s) deleted successfully"],
    )
    status_code: int = Field(default=200, examples=[200])
    data: dict = Field(
        default={},
        examples=[{}],
    )


# # +++++++++++++++++++++++++++++++++++++++ update message +++++++++++++++++++++++++++++++++++++++++

# update messages


class UpdateMessageDto(BaseModel):
    """
    Update message schema
    """

    conversation_id: str = Field(examples=["123124-1242-99999-5645765"])

    message: Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)] = (
        Field(examples=["Hello"])
    )

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values: dict) -> dict:
        """
        Validates fields
        """
        if isinstance(values, bytes):
            values = json.loads(values)
        message: str = values.get("message", "")

        if message:
            values["message"] = clean(message)

        return values


class UpdateMessageResponseDto(BaseModel):
    """
    Update message response schema
    """

    message: str = Field(
        default="message updated successfully",
        examples=["message updated successfully"],
    )
    status_code: int = Field(default=200, examples=[200])
    data: MessageBaseDto


# +++++++++++++++++++++++++++++++++++++++ mark message as read +++++++++++++++++++++++++++++++++++++++++
class MarkMessageAsReadDto(BaseModel):
    """
    Mark message as read schema
    """

    recipient_id: Annotated[
        str, StringConstraints(min_length=5, strip_whitespace=True)
    ] = Field(examples=["123124-1242-99999-5645765"])
    message_ids: List[str] = Field(examples=[["123124-1242-99999-5645765"]])

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values: dict) -> dict:
        """
        Validates fields
        """
        if isinstance(values, bytes):
            values = json.loads(values)
        message_ids: str = values.get("message_ids", [])
        recipient_id: str = values.get("recipient_id", "")

        if not isinstance(message_ids, list):
            raise ValueError("message_ids must be of type list/array")
        validated_message_ids = []
        for id_ in message_ids:
            validated_message_ids.append(clean(id_))

        values["message_ids"] = validated_message_ids

        if recipient_id:
            values["recipient_id"] = clean(recipient_id)

        return values


class MarkMessageAsReadResponse(BaseModel):
    """
    Mark message as read response schema
    """

    status_code: int = Field(default=200, examples=[200])
    message: str = Field(
        default="messages successfuly mark as read.",
        examples=["messages successfuly mark as read."],
    )
    data: dict = Field(default={}, examples=[{}])
