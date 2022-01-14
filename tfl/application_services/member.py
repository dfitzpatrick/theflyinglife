from typing import Optional, Generic, TypeVar

from tfl.domain.interfaces.members import IPasswordHandler, IMemberRepository
from tfl.domain.exceptions import MemberExists
from tfl.domain.member import UserCreateForm, Member

T = TypeVar("T")

class MemberService:

    def __init__(self, repo: IMemberRepository, password_handler: IPasswordHandler):
        self._repo = repo
        self._password_handler = password_handler

    async def create_member(self, data: UserCreateForm) -> Member:
        ...
        try:
            hashed_password = self._password_handler.hash(data.password)
            prepared_data = UserCreateForm(
                **data.dict(exclude={'password', 'confirm_password'}), password=hashed_password, confirm_password=hashed_password)
            member = await self._repo.create_member(prepared_data)
        except MemberExists:
            raise
        else:
            return member

    async def find_by_email(self, email: str) -> Optional[Member]:
        return await self._repo.find_by_email(email)

    async def find_by_id(self, identifier: T):
        return await self._repo.find_by_id(identifier)
