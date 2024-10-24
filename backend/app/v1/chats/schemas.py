from typing import List, Optional, Annotated
from datetime import datetime, timezone
from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    StringConstraints,
    model_validator
)
from bleach import clean
from unicodedata import normalize

class BaseMessage(BaseModel):
    """
    Schema for individual message.
    """
    room_id: str = Field(
        examples=["213e3d.415f5.h7j64..."]
    )
    content: str = Field(
        examples=["Good day to you."]
    )
    created_at: datetime = Field(
        examples=[datetime.now(tz=timezone.utc)]
    )
    username: str = Field(
        examples=["frech-prince"]
    )
    first_name: str = Field(
        examples=["Prince"]
    )
    last_name: str = Field(
        examples=["Zion"]
    )
    avatar_url: Optional[HttpUrl] = Field(
        examples=["https://example.com/image_url"]
    )

class AllMessagesResponse(BaseModel):
    """
    Schema for messages response.
    """
    status_code: int = Field(default=200, examples=[200])
    message: str = Field(
        default="Messages Retrieved Successfully",
        examples=["Messages Retrieved Successfully"]
    )
    data: List[BaseMessage]

class MessageDeleteSchema(BaseModel):
    """
    Class for deleting messages.
    """
    message_ids: List[int] = Field(
        examples=[1]
    )

class UpdateMessageInput(BaseModel):
    """
    Class for updating a message.
    """
    message: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=1
        )
    ]

    @model_validator(mode="before")
    @classmethod
    def validate_message(cls, values: dict):
        """
        Validates message.
        """
        message: str = values.get("message", "")

        if not message:
            raise ValueError("message cannot be empty")
        if len(message) < 2 and message.startswith(" "):
            raise ValueError("message cannot contain only a whitespace")
        if message.strip(" ") == "":
            raise ValueError("message cannot be empty")

        values["message"] = normalize("NFKC", clean(message))

        return values

class UpdateMessageResponse(AllMessagesResponse):
    """
    Class for message update response.
    """
    message: str = Field(
        default="Message updated successfully.",
        examples=["Message updated successfully."]
    )
    data: BaseMessage
