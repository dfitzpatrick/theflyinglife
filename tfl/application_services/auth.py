from tfl.domain.exceptions import AuthenticationError
from tfl.domain.member import Member
from tfl.domain.interfaces.members import IPasswordHandler, IMemberRepository


class AuthService:

    def __init__(self, repo: IMemberRepository, password_handler: IPasswordHandler):
        self._repo = repo
        self._password_handler = password_handler

    async def authenticate(self, email: str, password: str) -> Member:
        member = await self._repo.find_by_email(email)
        if member is None:
            raise AuthenticationError
        hashed_password = member.user.password
        if not self._password_handler.verify(password, hashed_password):
            raise AuthenticationError
        return member

    def hash_password(self, password: str) -> str:
        return self._password_handler.hash(password)
