"""
Room Member DTOs
"""

from typing import Optional, List
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
)


class RoomMemberBaseDto(BaseModel):
    """
    RoomMemberBaseDto
    """

    first_name: Optional[str] = Field(default=None, examples=["Johnson"])
    last_name: Optional[str] = Field(default=None, examples=["Dennis"])
    member_id: str = Field(
        default=None, examples=["222222222222-2222-2222-2222-22222222"]
    )
    profile_photo: Optional[str] = Field(default=None, examples=["https://image.com"])
    is_admin: bool = Field(examples=[False])

    model_config = ConfigDict(from_attributes=True)


class RoomMebersResponseDto(BaseModel):
    """
    RoomMebersResponseDto
    """

    status_code: int = Field(default=200, examples=[200])
    message: str = Field(
        default="Room Members fetched succesfully",
        examples=["Room Members fetched succesfully"],
    )
    data: List[Optional[RoomMemberBaseDto]]
