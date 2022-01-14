from pydantic.generics import GenericModel
from pydantic import BaseModel
from typing import TypeVar, Generic, NamedTuple

T = TypeVar("T")


class Entity(GenericModel, Generic[T]):
    id: T


class ValueObject(BaseModel):
    ...

    class Config:
        frozen = True


class Aggregate(BaseModel):
    ...

    class Config:
        frozen = True


class Form(BaseModel):

    class Config:
        frozen = True


class HeadAndTailString(NamedTuple):
    head: str
    tail: str