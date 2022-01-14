import typing

from starlette.authentication import AuthenticationBackend, AuthCredentials
from starlette.requests import HTTPConnection

from tfl.instances import member_service


class CookieSessionAuthentication(AuthenticationBackend):
    async def authenticate(self, conn: HTTPConnection) -> typing.Optional[typing.Tuple["AuthCredentials", "BaseUser"]]:
        if 'Authorization' in conn.headers:
            return
        user_id = conn.session.get('user_id')
        member = await member_service.find_by_id(user_id)
        print(f'Authentication Middleware: {member}')
        if member is None:
            return
        return AuthCredentials(["authenticated"]), member

