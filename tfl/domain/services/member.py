from tfl.domain.interfaces.members import ISessionObject
from tfl.domain.member import UserCreateForm, Member, Credentials
from tfl.instances import member_service
from tfl.instances import auth_service
from fastapi.requests import Request

async def register_member(model: UserCreateForm) -> None:
    """
    Domain service that will handle everything with registering a user.
    Right now its simply creating them.

    """
    await member_service.create_member(model)



async def login_member(request: ISessionObject, credentials: Credentials) -> Member:
    """Performs login logic. Raises AuthenticationError if not successful."""
    member = await auth_service.authenticate(credentials.email, credentials.password)
    request.session['user_id'] = member.user.id

