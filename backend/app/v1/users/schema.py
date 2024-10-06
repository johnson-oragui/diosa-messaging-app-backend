"""
pydantic models
"""
import unicodedata
import re
from typing import Annotated, Optional
from pydantic import (BaseModel,
                      ConfigDict,
                      model_validator,
                      StringConstraints,
                      EmailStr,
                      Field,
                      HttpUrl)
from email_validator import validate_email, EmailNotValidError
from bleach import clean
from datetime import datetime, timezone, date

from app.core.config import settings


TESTING = settings.test

if TESTING:
    TEST = True
else:
    TEST = False

class RegisterInput(BaseModel):
    email: Annotated[
        str,
        StringConstraints(
            min_length=11,
            strip_whitespace=True,
            strict=True
        )
    ] = Field(examples=['Johnson@example.com'])
    username: Annotated[
        str,
        StringConstraints(
            max_length=20,
            min_length=3,
            strip_whitespace=True,
            strict=True
        )
    ] = Field(examples=['Johnson1234'])
    first_name: Annotated[
        str,
        StringConstraints(
            max_length=20,
            min_length=3,
            strip_whitespace=True,
            strict=True
        )
    ] = Field(examples=['Johnson'])
    last_name: Annotated[
        str,
        StringConstraints(
            max_length=20,
            min_length=3,
            strip_whitespace=True,
            strict=True
        )
    ] = Field(examples=['Doe'])
    password: Annotated[
        str,
        StringConstraints(
            max_length=30,
            min_length=8,
            strip_whitespace=True,
            strict=True
        )
    ] = Field(examples=['Johnson1234@'])
    confirm_password: Annotated[
        str,
        StringConstraints(
            max_length=30,
            min_length=8,
            strip_whitespace=True,
            strict=True
        )
    ] = Field(examples=['Johnson1234@'])

    idempotency_key: Annotated[
        Optional[str],
        StringConstraints(
            max_length=120,
            min_length=6,
            strip_whitespace=True,
            strict=True
        )
    ] = Field(
        default=None,
        examples=["dij9048208293dj230"],
        description="Idempotency key(a hash of username and email)"
    )

    @classmethod
    def validate_names(cls, name: str, field: str) -> None:
        """
        Checks for white space
        """
        # offensive words
        offensive_words = [
            'fuck', 'ass', 'pussy', 'asshole'
        ]
        # reserved usernames
        reserved_usernames = [
            'admin', 'root', 'superuser', 'superadmin'
        ]
        # not allowed characters for username, first_name, and last_name
        name_disallowed_char = '1234567890!@~`#$%^&*()_+=-,.<>/?"\\|'

        if field == "username":
            name_disallowed_char = '!@~`#$%^&*()_+=,.<>/?"\\|'
            
            # check for reserved username
            if name in reserved_usernames:
                raise ValueError('Username is reserved and cannot be used')

        for c in name:
            if c == " ":
                raise ValueError(f'use of white space is not allowed in {field}')
            if c in name_disallowed_char:
                raise ValueError(f'{c} is not allowed in {field}')
        
        offensive_regex = r'\b(?:' + '|'.join(offensive_words) + r')\b'
        # check for offfensive words
        if re.search(offensive_regex, name):
            raise ValueError(f'{field} contains offensive language')

    @classmethod
    def validate_my_email(cls, email: str) -> Optional[str]:
        """
        Validates email.
        """
        # emails liable to fraud
        blacklisted_domains = [
            'example.com', 'mailinator.com', 'tempmail.com'
        ]
        email_domain = email.split('@')[1].lower()
        if email_domain in blacklisted_domains:
            raise ValueError(f'{email_domain} is not allowed for registration')
        try:
            email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            pattern = re.compile(email_regex)
            email = validate_email(
                email,
                check_deliverability=True,
                test_environment=TEST
            ).normalized
            if not pattern.match(email):
                raise ValueError(f'{email} is invalid')
            return email
        except EmailNotValidError as exc:
            raise ValueError(str(exc))

    @classmethod
    def validate_password(cls, password: str) -> None:
        """
        Validates password.
        """
        # allowed special characters for password
        password_allowed = '!@#&-_,.'

        if not any(char for char in password if char.islower()):
            raise ValueError(f'{password} must contain at least one lowercase letter')
        if not any(char for char in password if char.isupper()):
            raise ValueError(f'{password} must contain at least one uppercase letter')
        if not any(char for char in password if char.isdigit()):
            raise ValueError(f'{password} must contain at least one digit character')
        if not any(char for char in password if char in password_allowed):
            raise ValueError(f'{password} must contain at least one of these special characters {password_allowed}')
        if any(char for char in password if char == ' '):
            raise ValueError(f"{password} cannot contain a white space character")

    @model_validator(mode='before')
    @classmethod
    def validate_fields(cls, values: dict):
        """
        Validates all fields
        """
        password: str = values.get('password', '')
        confirm_password = values.get('confirm_password', '')
        email: EmailStr = values.get('email', '')
        first_name: str = values.get('first_name', '')
        last_name: str = values.get('last_name', '')
        username: str = values.get('username', '')

        if not email:
            raise ValueError("email must be provided")

        if password != confirm_password:
            raise ValueError('Passwords must match')

        cls.validate_password(password)

        cls.validate_names(first_name, "first_name")
        cls.validate_names(last_name, "last_name")
        cls.validate_names(username, "username")

        values['first_name'] = unicodedata.normalize('NFKC', clean(first_name.lower()))
        values['last_name'] = unicodedata.normalize('NFKC', clean(last_name.lower()))
        values['username'] = unicodedata.normalize('NFKC', clean(username.lower()))

        values['email'] = cls.validate_my_email(email)

        return values

class UserBase(BaseModel):
    """
    User Base model
    """
    id: str = Field(examples=['1234ed.4455tf...'])
    email: str = Field(examples=['Johnson@example.com'])
    username: str = Field(examples=['Johnson1234'])
    first_name: str = Field(examples=['Johnson'])
    last_name: str = Field(examples=['Doe'])
    status: str = Field(examples=["active"])
    created_at: datetime = Field(examples=[datetime.now(timezone.utc)])
    updated_at: datetime = Field(examples=[datetime.now(timezone.utc)])

    model_config = ConfigDict(from_attributes=True)

class ProfileBase(BaseModel):
    """
    ProfileBase
    """
    id: str = Field(examples=["a0c96829-e826-4ab3-90f6-55b6c9a533bb"])
    DOB: Optional[date] = Field(
        examples=[str(date.fromisocalendar(2024, 2, 3))]
    )
    gender: Optional[str] = Field(examples=["male"])
    recovery_email: Optional[EmailStr] = Field(
        examples=["myemail@email.com"]
    )
    bio: Optional[str] = Field(
        default=None,
        examples=["I am a very known ..."]
    )
    profession: Optional[str] = Field(
        default=None,
        examples=["Engineer"]
    )
    avatar_url: Optional[HttpUrl] = Field(
        default=None,
        examples=["https://example.com/image"]
    )
    facebook_link: Optional[HttpUrl] = Field(
        default=None,
        examples=["https://example.com"]
    )
    x_link: Optional[HttpUrl] = Field(
        default=None,
        examples=["https://example.com"]
    )
    instagram_link: Optional[HttpUrl] = Field(
        default=None,
        examples=["https://example.com"]
    )
    created_at: datetime = Field(examples=[datetime.now(timezone.utc)])
    updated_at: datetime = Field(examples=[datetime.now(timezone.utc)])

class UserProfile(BaseModel):
    """
    User data and profile data
    """
    user: UserBase
    profile: ProfileBase

    model_config = ConfigDict(from_attributes=True)

class RegisterOutput(BaseModel):
    """
    Registration client response model
    """
    status_code: int = Field(examples=[201])
    message: str = Field(examples=['User Refgistered Successfully'])
    data: UserProfile

class UserMeOut(BaseModel):
    """
    Model for UserMeOut.
    """
    status_code: int = Field(
        examples=[200],
    )
    message: str = Field(examples=["User Data Retrieved Successfully"])
    data: UserProfile

class LoginInput(BaseModel):
    """
    Model for login input
    """
    username: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=3
        )
    ]
    password: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=6,
            max_length=30
        )
    ]

class LoginOut(BaseModel):
    """
    Model for Login response.
    """
    status_code: int = Field(
        examples=[200],
    )
    message: str = Field(examples=["Login Successful"], default="Login Successful")
    data: UserProfile


__all__ = [
    "UserMeOut", "RegisterOutput",
    "UserProfile", "ProfileBase",
    "UserBase", "RegisterInput",
    "LoginOut"
]
