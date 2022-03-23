import os.path

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from fastapi.templating import Jinja2Templates

from tfl.domain.services.core import open_markdown
from tfl.instances import metar_service, taf_service
from pathlib import Path
import random

BASE_DIR = Path(__file__).resolve()

SITE_DIR = BASE_DIR.parent.parent
markdown_dir = f'{SITE_DIR}/markdown/airports'
templates = Jinja2Templates(directory=F"{SITE_DIR}/templates")


def aerial(icao: str) -> str:
    icao = icao.lower()
    static_path = '/static/img/aerials'
    airport_aerials = str(SITE_DIR) + static_path
    fn = f'{airport_aerials}/{icao}.png'
    print(f'Checking: {fn}')
    random_img = random.choice(os.listdir(f'{airport_aerials}/random'))
    return f'{static_path}/{icao}.png' if os.path.exists(fn) else f'/static/img/aerials/random/{random_img}'


class AirportsView(HTTPEndpoint):

    async def get(self, request: Request):
        icao = request.path_params['icao']
        metar = await metar_service.metar(icao)
        taf = await taf_service.taf(icao)

        try:
            content = open_markdown(f'{markdown_dir}/{icao}.md')
        except FileNotFoundError:
            content = ""

        location = None
        if metar is not None:
            location = metar.location
        elif taf is not None:
            location = taf.location

        return templates.TemplateResponse("airports.html", {
            "icao": icao,
            "request": request,
            "metar": metar,
            "taf": taf,
            "location": location,
            "content": content,
            'aerial': aerial(icao)
        })
