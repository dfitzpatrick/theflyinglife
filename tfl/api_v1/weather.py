from fastapi.routing import APIRouter

from tfl.instances import metar_service, taf_service

router = APIRouter()


@router.get("/metar/{icao}")
async def metar_get(icao: str):
    metar = await metar_service.metar(icao)
    return metar


@router.get("/taf/{icao}")
async def taf_get(icao: str):
    taf = await taf_service.taf(icao)
    return taf
