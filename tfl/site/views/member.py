from pathlib import Path

from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from pydantic_forms import PydanticForm
from starlette.authentication import requires
from starlette.endpoints import HTTPEndpoint
from starlette.responses import RedirectResponse
from starlette.routing import Route

from tfl.domain.exceptions import MemberExists, AuthenticationError
from tfl.domain.member import UserCreateForm, LoginForm, Credentials
from tfl.domain.services.member import register_member, login_member

BASE_DIR = Path(__file__).resolve()
SITE_DIR = BASE_DIR.parent.parent
templates = Jinja2Templates(directory=F"{SITE_DIR}/templates")


class RegisterPage(HTTPEndpoint):

    async def get(self, request: Request):
        form = await PydanticForm.create(request, UserCreateForm)
        return templates.TemplateResponse('member/register.html', {
            'request': request, 'form': form, 'message': ''
        })

    async def post(self, request: Request):
        form = await PydanticForm.validate_request(request, UserCreateForm)
        message = ''
        if form.is_valid:
            try:
                await register_member(form.model)
                await login_member(request, Credentials(
                    email=form.model.email,
                    password=form.model.password
                ))
                return RedirectResponse(request.url_for('profile'), status_code=302)
            except MemberExists:
                message = 'This account already exists'

        return templates.TemplateResponse('member/register.html', {
            'request': request, 'form': form, 'message': message
        })


class LoginPage(HTTPEndpoint):

    async def get(self, request: Request):
        form = await PydanticForm.create(request, LoginForm)
        return templates.TemplateResponse('member/login.html', {'request': request, 'form': form})

    async def post(self, request: Request):
        form = await PydanticForm.validate_request(request, LoginForm)
        message = ''
        if form.is_valid:
            try:
                await login_member(request, Credentials(
                    email=form.model.email,
                    password=form.model.password
                ))
                RedirectResponse(request.url_for('member:profile'))
            except AuthenticationError:
                message = 'Invalid Credentials'

        return templates.TemplateResponse('member/login.html', {
            'request': request, 'form': form, 'message': message
        })


class ProfilePage(HTTPEndpoint):

    async def get(self, request: Request):
        return templates.TemplateResponse('member/profile.html', {
            'request': request,
            'member': request.user
        })


