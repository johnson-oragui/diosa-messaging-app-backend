"""
Register DTOs
"""

import json
import os
from typing import Annotated, Optional
import re
from email_validator import validate_email, EmailNotValidError
from pydantic import (
    BaseModel,
    model_validator,
    StringConstraints,
    EmailStr,
    Field,
)

from app.dto.v1.user_dto import UserBaseDto

TEST = False
if os.getenv("TEST", None):
    TEST = True


def validate_user_email(email: str) -> Optional[str]:
    """
    Validates email.
    """
    if not email:
        raise ValueError("email must be provided.")
    if "@" not in email:
        raise ValueError("invalid email address.")
    # emails liable to fraud
    blacklisted_domains = ["example.com", "mailinator.com", "tempmail.com"]
    email_domain = email.split("@")[1].lower()
    if email_domain in blacklisted_domains:
        raise ValueError(f"{email_domain} is not allowed for registration")
    try:
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        pattern = re.compile(email_regex)
        email = validate_email(
            email, check_deliverability=True, test_environment=TEST
        ).normalized
        if not pattern.match(email):
            raise ValueError(f"{email} is invalid")
        return email
    except EmailNotValidError as exc:
        raise ValueError(str(exc)) from exc


def validate_password(password: str | None) -> None:
    """
    Validates password.
    """
    if not password:
        raise ValueError("password must be provided")
    # allowed special characters for password
    password_allowed = "!@#&-_,."
    not_allowed = "+="  # Original not_allowed string

    # Adding all special characters
    special_chars = r'"$%\'()*+,./:;<=>?[\\]^`{|}~'
    not_allowed += special_chars

    if not any(char for char in password if char.islower()):
        raise ValueError("password must contain at least one lowercase letter")
    if not any(char for char in password if char.isupper()):
        raise ValueError("password must contain at least one uppercase letter")
    if not any(char for char in password if char.isdigit()):
        raise ValueError("password must contain at least one digit character")
    if not any(char for char in password if char in password_allowed):
        raise ValueError(
            f"password must contain at least one of these special characters {password_allowed}"
        )
    if any(char for char in password if char == " "):
        raise ValueError("password cannot contain a white space character")
    if any(char in not_allowed for char in password):
        raise ValueError(
            f"contains invalid characters. Allowed special characters: {password_allowed}"
        )


class RegisterUserRequestDto(BaseModel):
    """
    RegisterUserRequestDto
    """

    email: EmailStr = Field(examples=["johnson@gmail.com"])

    idempotency_key: Annotated[
        str, StringConstraints(min_length=3, max_length=60, strip_whitespace=True)
    ] = Field(default=None, examples=["123456789012-1234-1234-1234-12345678"])
    password: Annotated[
        str, StringConstraints(min_length=8, max_length=64, strip_whitespace=True)
    ] = Field(examples=["Johnson1234#"])
    confirm_password: Annotated[
        str, StringConstraints(min_length=8, max_length=64, strip_whitespace=True)
    ] = Field(examples=["Johnson1234#"])

    @model_validator(mode="before")
    @classmethod
    def validate_password(cls, values: dict):
        """
        Validates fields
        """
        if isinstance(values, bytes):
            values = json.loads(values)
        password: str = values.get("password", "")

        email: str = values.get("email", "")
        confirm_password = values.get("confirm_password")

        validate_password(password)
        if password != confirm_password:
            raise ValueError("Passwords must match")

        if not email:
            raise ValueError("email must be provided")

        values["email"] = validate_user_email(email.lower())

        return values


class RegisterOutputResponseDto(BaseModel):
    """
    RegisterOutputResponseDto
    """

    status_code: int = Field(examples=[201], default=201)
    message: str = Field(
        default="User Registered Successfully",
        examples=["User Registered Successfully"],
    )
    data: UserBaseDto


# ++++++++++++++++++++++ authenticate +++++++++++++++++++++++++++
class AuthenticateUserRequestDto(BaseModel):
    """
    RegisterUserRequestDto
    """

    email: Optional[EmailStr] = Field(default=None, examples=["johnson@gmail.com"])

    username: Optional[
        Annotated[
            str, StringConstraints(min_length=1, max_length=38, strip_whitespace=True)
        ]
    ] = Field(default=None, examples=["Johnson1234"])
    password: Annotated[
        str, StringConstraints(min_length=8, max_length=64, strip_whitespace=True)
    ] = Field(examples=["Johnson1234#"])
    session_id: Annotated[
        str, StringConstraints(min_length=32, max_length=38, strip_whitespace=True)
    ] = Field(examples=["123456789012-1234-1234-1234-12345678"])

    @model_validator(mode="before")
    @classmethod
    def validate_password(cls, values: dict):
        """
        Validates fields
        """
        if isinstance(values, bytes):
            values = json.loads(values)
        password: str | None = values.get("password", None)

        email: str | None = values.get("email", None)
        username: str | None = values.get("username", None)

        validate_password(password)
        if (not username and not email) or (username and email):
            raise ValueError("must provide either username or email")

        if email:
            values["email"] = validate_user_email(email.lower())
        if username:
            values["username"] = username.lower()

        return values


class AccessTokenDto(BaseModel):
    """Access token dto"""

    token: str = Field(examples=["ee23e23e2r.4r435t54t46t6yy5634444444"])
    expire_at: int = Field(examples=[1787878787878782])


class AuthenticationBaseDto(BaseModel):
    """
    Authentication Base dto
    """

    access_token: AccessTokenDto
    user_data: UserBaseDto


class AuthenticateUserResponseDto(BaseModel):
    """
    Authenicate User response
    """

    status_code: int = Field(default=200, examples=[200])
    message: str = Field(default="Login success", examples=["Login success"])
    data: AuthenticationBaseDto


# +++++++++++++++++++++++++== logout ++++++++++++++++++++++++++++++++++
class LogoutResponseDto(BaseModel):
    """
    Logout response
    """

    status_code: int = Field(default=200, examples=[200])
    message: str = Field(default="Logout success", examples=["Logout success"])
    data: dict = Field(default={}, examples=[{}])


# +++++++++++++++++++++++++== refresh token ++++++++++++++++++++++++++++++++++
class RefreshTokenResponseDto(BaseModel):
    """
    Refresh token dto
    """

    status_code: int = Field(default=200, examples=[200])
    message: str = Field(
        default="Tokens refresh successful", examples=["Tokens refresh successful"]
    )
    data: AccessTokenDto
