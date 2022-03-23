from typing import List, Generic, TypeVar, Dict, Any, Sequence, Optional
from pydantic import EmailStr

from tfl.domain.exceptions import NoMember, MemberExists
from tfl.domain.member import Member, UserCreateForm, User
from tfl.domain.interfaces.members import IMemberRepository

T = TypeVar("T")


class InMemoryMemberRepository(IMemberRepository, Generic[T]):

    def __init__(self, id_factory: List = range(1, 100)):
        self.members: Dict[T, Member] = {}
        self.id_factory = list(id_factory)

    async def all(self) -> List[Member]:
        return list(self.members.values())

    async def find_by_email(self, email: EmailStr) -> Optional[Member]:
        for member in self.members.values():
            if member.user.email == email:
                return member

    async def find_by_id(self, identifier: T) -> Optional[Member]:
        for member in self.members.values():
            if member.user.id == identifier:
                return member

    async def create_member(self, data: UserCreateForm) -> Member:
        if data.email in [m.user.email for m in self.members.values()]:
            raise MemberExists
        new_id = self.id_factory.pop()
        user = User(
            id=new_id,
            email=data.email,
            password=data.password
        )
        member = Member(
            user=user,
            name=data.name,
            home_airport=data.home_airport
        )
        self.members[new_id] = member
        return member

    async def update_member(self, member: Member) -> None:
        id = member.user.id
        if id not in self.members.keys():
            raise NoMember
        self.members[id] = member

