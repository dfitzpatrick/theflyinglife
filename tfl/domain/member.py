from pydantic import EmailStr, validator
from starlette.authentication import BaseUser

from tfl.domain.core import Entity, Aggregate, Form


class Password(str):
    minimum_length = 6
    num_capitals = 1

    def __init__(self, value):
        str.__init__(value)

    @classmethod
    def must_meet_length_requirements(cls, value, field, config):
        if len(value) < cls.minimum_length:
            raise ValueError(f"Passwords must be at least {cls.minimum_length} characters")
        return value

    @classmethod
    def must_meet_capitalization_requirements(cls, value, field, config):
        if sum(1 for c in value if c.isupper()) < cls.num_capitals:
            raise ValueError(f"Passwords must have at least {cls.num_capitals} capital letter(s)")
        return value

    @classmethod
    def __get_validators__(cls):
        yield cls.must_meet_length_requirements
        yield cls.must_meet_capitalization_requirements


class Name(str):
    minimum_length = 1

    def __init__(self, value):
        str.__init__(value)

    @classmethod
    def must_meet_length_requirements(cls, value, field, config):
        if len(value) < cls.minimum_length:
            raise ValueError(f"Passwords must be at least {cls.minimum_length} characters")
        return value

    @classmethod
    def __get_validators__(cls):
        yield cls.must_meet_length_requirements


class ICAO(str):

    def __init__(self, value):
        str.__init__(value)


class User(Entity[int]):
    email: EmailStr
    password: Password
    is_superuser: bool = False
    is_active: bool = True


class Credentials(Aggregate):
    email: EmailStr
    password: Password


class Member(Aggregate, BaseUser):
    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.name

    @property
    def identity(self) -> str:
        return str(self.user.id)

    user: User
    name: Name
    home_airport: ICAO
    looking_to_fly: bool = False
    looking_for_partners: bool = False


class UserCreateForm(Form):
    email: EmailStr
    password: Password
    confirm_password: Password
    name: Name
    home_airport: ICAO

    @validator('confirm_password')
    def confirm_password_must_match_password(cls, value, values):
        print(values)
        print(value)
        if values['password'] != value:
            raise ValueError("Passwords must match")
        return value


class LoginForm(Form):
    email: EmailStr
    password: Password

