from fastapi.routing import APIRouter

from tfl.instances import metar_service, taf_service, airport_repository

router = APIRouter()


@router.get("/metar/{icao}")
async def metar_get(icao: str):
    metar = await metar_service.metar(icao)
    return metar


@router.get("/taf/{icao}")
async def taf_get(icao: str):
    taf = await taf_service.taf(icao)
    return taf


@router.get('/airport/{icao}')
async def airport_get(icao: str):
    airport = await airport_repository.find(icao)
    return airport
