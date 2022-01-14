from abc import ABC, abstractmethod, abstractproperty
from typing import Protocol, List, Optional, Dict, Any, Generic, TypeVar
from tfl.domain.member import Member, UserCreateForm

T = TypeVar("T")


class IPasswordHandler(Protocol):

    def verify(self, password: str, hashed_password: str) -> bool:
        ...

    def hash(self, password: str) -> str:
        ...


class IMemberRepository(ABC, Generic[T]):

    @abstractmethod
    async def all(self) -> List[Member]:
        ...

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[Member]:
        ...

    @abstractmethod
    async def create_member(self, data: UserCreateForm) -> Member:
        ...

    @abstractmethod
    async def update_member(self, member: Member) -> None:
        ...

    @abstractmethod
    async def find_by_id(self, identifier: T) -> Optional[Member]:
        ...


class ISessionObject(Protocol):
    session: Dict[str, Any]