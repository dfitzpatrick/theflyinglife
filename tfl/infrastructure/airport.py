from typing import Optional, Dict

from tfl.domain.exceptions import EntityExistsError, EntityNotFoundError
from tfl.domain.facilities import Airport
from tfl.domain.interfaces.facility import IAirportRepository


class AirportRepository(IAirportRepository):

    def __init__(self):
        self.repo: Dict[str, Airport] = {}

    async def create(self, airport: Airport) -> None:
        icao = airport.icao.lower()
        if icao in self.repo.keys():
            raise EntityExistsError(f"{icao} already in repository")
        self.repo[icao] = airport

    async def update(self, airport: Airport):
        try:
            self.repo[airport.icao.lower()] = airport
        except KeyError:
            raise EntityNotFoundError(f"{airport.icao} not found.")

    async def find(self, icao: str) -> Optional[Airport]:
        try:
            return self.repo[icao.lower()]
        except KeyError:
            raise EntityNotFoundError(f"{icao} not found.")

    async def delete(self, icao: str) -> None:
        try:
            del self.repo[icao]
        except KeyError:
            raise EntityNotFoundError(f"{icao} not found.")