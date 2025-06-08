"""
Direct conversation dto
"""

from typing import List, Optional
import json

from pydantic import BaseModel, Field, model_validator
from bleach import clean


class ConversationBaseDto(BaseModel):
    """
    Schema for all conversations
    """

    conversation_id: Optional[str] = Field(
        default=None, examples=["312423-4-3544354-5-465"]
    )
    user_id: Optional[str] = Field(default=None, examples=["222222-4-3544354-5-465"])
    profile_photo: Optional[str] = Field(
        default=None, examples=["https://profile_photo.com/something.jpg"]
    )
    firstname: Optional[str] = Field(default=None, examples=["Johnson"])
    last_message: Optional[str] = Field(default=None, examples=["Hello Johnson"])
    unread_message_count: int = Field(default=0, examples=["Hello Johnson"])


# +++++++++++++++++++++++++++++++++++++++ all conversations +++++++++++++++++++++++++++++++++++++++++


class AllConversationsResponseDto(BaseModel):
    """
    All  Conversations schema
    """

    message: str = Field(
        default="Conversations retrieved successfully",
        examples=["Conversations retrieved successfully"],
    )
    status_code: int = Field(default=200, examples=[200])
    page: int = Field(default=1, examples=[1])
    limit: int = Field(default=20, examples=[20])
    total_pages: int = Field(examples=[10])
    total_conversations: int = Field(examples=[100])

    data: List[Optional[ConversationBaseDto]]


# +++++++++++++++++++++++++++++++++++++++ delete conversations +++++++++++++++++++++++++++++++++++++++++


class DeleteConversationsDto(BaseModel):
    """
    Schema for conversation delete
    """

    conversation_ids: List[str] = Field(
        examples=[["12312432-42345435-4564645", "1234324-23453-53454-645"]]
    )

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values: dict) -> dict:
        """
        Validates fields
        """
        if isinstance(values, bytes):
            values = json.loads(values)

        conversation_ids = values.get("conversation_ids", [])

        if not isinstance(conversation_ids, list):
            raise ValueError("conversation_ids must be of type list/array")
        validated_conversation_ids = []
        for id_ in conversation_ids:
            validated_conversation_ids.append(clean(id_))

        values["message_ids"] = validated_conversation_ids
        return values


class DeleteConversationsResponseDto(BaseModel):
    """
    Delete message schema
    """

    message: str = Field(
        default="Conversation(s) removed successfully",
        examples=["Conversation(s) removed successfully"],
    )
    status_code: int = Field(default=200, examples=[200])
    data: dict = Field(
        default={},
        examples=[{}],
    )
