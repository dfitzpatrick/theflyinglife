from fastapi.routing import APIRouter
from tfl.instances import taf_repository
from tfl.domain.weather import TAF

router = APIRouter()

@router.get("/tafs", response_model=list[TAF])
async def list_tafs(offset: int = 0, limit: int = 50, stations: str | None = None):
    return await taf_repository.all(offset, limit, stations)

@router.get('/tafs/longest', response_model=list[TAF])
async def list_longest_tafs(offset: int = 0, limit: int = 10, stations: str | None = None):
    sorting = (lambda o: len(o.raw_text), True)
    return await taf_repository.all(
        offset=offset, 
        limit=limit, 
        stations=stations, 
        sorting=sorting
    )

@router.get("/tafs/{icao}", response_model=list[TAF])

async def get_icao_tafs(icao: str):
    # TODO: Store multiple metars. Simulate response
    return [await taf_repository.find(icao)]

@router.get("/tafs/{icao}/latest", response_model=TAF)
async def get_icao_latest_taf(icao: str):
    return await taf_repository.find(icao)