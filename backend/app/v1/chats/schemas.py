from typing import List, Optional
from datetime import datetime, timezone
from pydantic import (
    BaseModel,
    Field,
    HttpUrl
)

class BaseMessage(BaseModel):
    """
    Schema for individual message.
    """
    room_id: str = Field(
        examples=["Messages Retrieved Successfully"]
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
