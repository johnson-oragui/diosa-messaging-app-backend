"""
Room Member DTOs
"""

from typing import Optional, List, Annotated
import json
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    StringConstraints,
    model_validator,
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


# +++++++++++++++++++++++++ Remove/make admin Room Member ++++++++++++++++++++++++++++


class UpdateRoomMemberRequestDto(BaseModel):
    """
    Update room member
    """

    member_id: Annotated[
        str, StringConstraints(min_length=20, max_length=40, strip_whitespace=True)
    ] = Field(examples=["121212121212-1212-2121-2121-21212121"])
    is_admin: Optional[bool] = Field(default=None, examples=[True])
    remove_member: Optional[bool] = Field(default=None, examples=[True])

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values: dict) -> dict:
        """
        Validate fields
        """
        if isinstance(values, bytes):
            values = json.loads(values)

        is_admin: bool | None = values.get("is_admin")
        remove_member: bool | None = values.get("remove_member")

        if remove_member is None and is_admin is None:
            raise ValueError("remove_member and is_admin cannot be null")
        return values


class UpdateRoomMemberResponseDto(BaseModel):
    """
    Update RoomMember ResponseDto
    """

    status_code: int = Field(default=200, examples=[200])
    message: str = Field(
        default="Room Member updated succesfully",
        examples=["Room Member updated succesfully"],
    )
    data: dict = Field(default={}, examples=[{}])
