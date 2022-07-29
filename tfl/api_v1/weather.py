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


@router.get("/taf/{icao}")
async def taf_get(icao: str):
    taf = await taf_service.taf(icao)
    return taf


@router.get('/airport/{icao}')
async def airport_get(icao: str):
    airport = await airport_repository.find(icao)
    return airport

@router.get('/plates/{icao}')
async def plates_get(icao: str, name: Optional[str] = None) -> List[FAAPlate]:
    airport = await airport_repository.find(icao)
    plates = airport.plates
    if name is None:
        return plates
    plate_names = [p.name.lower() for p in plates]
    best_plates = get_best_plates(name.lower(), plate_names)
    print(best_plates)
    return [p for p in plates if p.name.lower() in best_plates]