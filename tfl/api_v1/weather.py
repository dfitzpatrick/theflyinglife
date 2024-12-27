from typing import Optional, List

from fastapi.routing import APIRouter

from tfl.domain.facilities import FAAPlate
from tfl.domain.services.weather import get_best_plates
from tfl.instances import metar_service, taf_service, airport_repository

router = APIRouter()


@router.get("/metar/{icao}")
async def metar_get(icao: str):
    metar = await metar_service.metar(icao)
    return metar

@router.get('/metar')
async def metar_qs(longest: int):
    metars = await metar_service.find_longest_metars(longest)
    return metars

@router.get("/taf/{icao}")
async def taf_get(icao: str):
    taf = await taf_service.taf(icao)
    return taf


@router.get('/airport/{icao}')
async def airport_get(icao: str):
    airport = await airport_repository.find(icao)
    return airport

@router.get('/plates')
async def plates_get_main(icao_only: bool = False, limit: int = 20, offset: int = 0):
    airports = await airport_repository.all()
    if icao_only:
        icaos = []
        for airport in airports:
            for plate in airport.plates:
                if plate.icao not in icaos:
                    icaos.append(plate.icao)
        return icaos
    plates: List[FAAPlate] = [plate for airport in airports for plate in airport.plates]
    return plates[offset:limit+offset]

@router.get('/plates/{icao}')
async def plates_get(icao: str, name: Optional[str] = None) -> List[FAAPlate]:
    airport = await airport_repository.find(icao)
    plates = airport.plates
    if name is None:
        return plates
    return [p for p in plates if name.lower() in p.name.lower()]



