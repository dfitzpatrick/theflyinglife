from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.sessions import SessionMiddleware
from tfl.configuration import SECRET_KEY
from tfl.infrastructure.auth import CookieSessionAuthentication

installed_middleware = [
    Middleware(SessionMiddleware, secret_key=SECRET_KEY),
    Middleware(AuthenticationMiddleware, backend=CookieSessionAuthentication())

]