from pydantic.generics import GenericModel
from pydantic import BaseModel
from typing import TypeVar, Generic, NamedTuple

T = TypeVar("T")


class TFLModel(BaseModel):
    """
            Workaround for serializing properties with pydantic until
            https://github.com/samuelcolvin/pydantic/issues/935
            is solved
            """
    @classmethod
    def get_properties(cls):
        return [
            prop for prop in dir(cls)
            if isinstance(getattr(cls, prop), property) and prop not in ("__values__", "fields")
        ]

    def dict(self, *args, **kwargs) -> 'DictStrAny':
        self.__dict__.update({prop: getattr(self, prop) for prop in self.get_properties()})

        return super().dict(*args, **kwargs)


class Entity(GenericModel, Generic[T]):
    id: T


class ValueObject(TFLModel):
    ...

    class Config:
        frozen = True


class Aggregate(TFLModel):
    ...

    class Config:
        frozen = False


class Form(TFLModel):

    class Config:
        frozen = True


class HeadAndTailString(NamedTuple):
    head: str
    tail: str