from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from pydantic_forms import PydanticForm
from tfl.domain.services.core import open_markdown
from tfl.domain.weather import ICAOSearchForm
from tfl.instances import metar_service, taf_service
from pathlib import Path

BASE_DIR = Path(__file__).resolve()

SITE_DIR = BASE_DIR.parent.parent

templates = Jinja2Templates(directory=F"{SITE_DIR}/templates")


class MainView(HTTPEndpoint):

    async def get(self, request: Request):
        icao_form = await PydanticForm.create(request, ICAOSearchForm)
        return templates.TemplateResponse("test.html", {
            "request": request,
            "icao_form": icao_form

        })

    async def post(self, request: Request):
        form = await PydanticForm.validate_request(request, ICAOSearchForm)
        if form.is_valid:
            icao = form.model.icao
            return RedirectResponse(f'/airports/{icao}', status_code=302)

        return templates.TemplateResponse("main.html", {
            "request": request,
            "icao_form": form
        })
