from fastapi.routing import APIRouter
from tfl.instances import airport_repository
from tfl.domain.weather import TAF

router = APIRouter()

@router.get("/procedures/{icao}")
async def list_icao_procedures(icao: str, name: str | None = None):
    airport = await airport_repository.find(icao)
    procedures = airport.plates
    if name is not None:
        procedures = [p for p in procedures if name.lower() in p.name.lower()]
    return procedures

