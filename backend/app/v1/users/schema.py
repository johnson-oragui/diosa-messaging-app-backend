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
                      Field)
from email_validator import validate_email, EmailNotValidError
from bleach import clean

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
        name_disallowed_char = '1234567890!@~`#$%^&*()_+=-,.<>/?"\|'

        if field == "username":
            name_disallowed_char = '!@~`#$%^&*()_+=,.<>/?"\|'
            
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

    model_config = ConfigDict(from_attributes=True)

class RegisterOutput(BaseModel):
    """
    Registration client response model
    """
    status_code: int = Field(examples=[201])
    message: str = Field(examples=['User Refgistered Successfully'])
    data: UserBase
