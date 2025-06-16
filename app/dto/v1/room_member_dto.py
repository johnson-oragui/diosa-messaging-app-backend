"""
Room Member DTOs
"""

from typing import Optional, List, Annotated
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    StringConstraints,
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


# +++++++++++++++++++++++++ Add Room Member ++++++++++++++++++++++++++++
class AddRoomMemberRequestDto(BaseModel):
    """
    Add room member
    """

    member_id: Annotated[
        str, StringConstraints(min_length=20, max_length=40, strip_whitespace=True)
    ] = Field(examples=["121212121212-1212-2121-2121-21212121"])
    is_admin: bool = Field(examples=[True])


class AddRoomMemberResponseDto(BaseModel):
    """
    AddRoomMemberResponseDto
    """

    status_code: int = Field(default=201, examples=[201])
    message: str = Field(
        default="Room Member added succesfully",
        examples=["Room Member added succesfully"],
    )
    data: dict = Field(default={}, examples=[{}])
