from typing import Dict, Optional

from tfl.domain.weather import TAF
from tfl.domain.exceptions import EntityNotFoundError, EntityExistsError
from tfl.domain.interfaces.weather import ITAFRepository


class TAFRepository(ITAFRepository):

    def __init__(self):
        self.repo: Dict[str, TAF] = {}

    async def create(self, taf: TAF) -> None:
        icao = taf.station_id.lower()
        if icao in self.repo.keys():
            raise EntityExistsError(f"{icao} already in repository")
        self.repo[icao] = taf

    async def update(self, taf: TAF) -> TAF:
        try:
            self.repo[taf.station_id.lower()] = taf
            return taf
        except KeyError:
            raise EntityNotFoundError(f"{taf.station_id} not found.")

    async def find(self, icao: str) -> Optional[TAF]:
        try:
            return self.repo[icao.lower()]
        except KeyError:
            raise EntityNotFoundError(f"{icao} not found.")

    async def delete(self, taf: TAF) -> None:
        try:
            del self.repo[taf.station_id.lower()]
        except KeyError:
            raise EntityNotFoundError(f"{icao} not found.")


