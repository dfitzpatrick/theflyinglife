from fastapi.routing import APIRouter
from tfl.instances import metar_repository
from tfl.domain.weather import Metar

router = APIRouter()

@router.get("/metars", response_model=list[Metar])
async def list_metars(offset: int = 0, limit: int = 50, stations: str | None = None):
    return await metar_repository.all(offset, limit, stations)

@router.get('/metars/longest', response_model=list[Metar])
async def list_longest_metars(offset: int = 0, limit: int = 10, stations: str | None = None):
    sorting = (lambda o: len(o.raw_text), True)
    return await metar_repository.all(
        offset=offset, 
        limit=limit, 
        stations=stations, 
        sorting=sorting
    )

@router.get("/metars/{icao}", response_model=list[Metar])

async def get_icao_metars(icao: str):
    # TODO: Store multiple metars. Simulate response
    return [await metar_repository.find(icao)]

@router.get("/metars/{icao}/latest", response_model=Metar)
async def get_icao_latest_metar(icao: str):
    return await metar_repository.find(icao)

