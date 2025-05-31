import typing
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class UserBaseDto(BaseModel):
    """
    UserBaseDto
    """

    id: str = Field(examples=["j099w9i8e43-23e3-4re4-56t5-67y3-893w2345"])
    email: str = Field(examples=["johnson@gmail.com"])
    first_name: typing.Union[str, None] = Field(default=None, examples=[None])
    last_name: typing.Union[str, None] = Field(default=None, examples=[None])
    username: typing.Union[str, None] = Field(default=None, examples=[None])
    created_at: datetime = Field(examples=[datetime.now()])
    profile_photo: typing.Union[str, None] = Field(default=None, examples=[None])

    model_config = ConfigDict(from_attributes=True)
