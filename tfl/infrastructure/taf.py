from typing import Dict, Optional

from tfl.domain.weather import TAF
from tfl.domain.exceptions import EntityNotFoundError, EntityExistsError
from tfl.domain.interfaces.weather import ITAFRepository
import logging
from typing import Any

log = logging.getLogger(__name__)

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
        icao = taf.station_id.lower()
        try:
            del self.repo[icao]
        except KeyError:
            raise EntityNotFoundError(f"{icao} not found.")


    async def all(self, offset: int = 0, limit: int = 50, stations: str | None = None, sorting: tuple[Any, bool] | None = None):
        """
        Return all Metars in the repository, paginated.
        """
        values = sorted(self.repo.values(), key=sorting[0], reverse=sorting[1]) if sorting else self.repo.values()
        if stations:
            stations = stations.split(',')
            tafs = [taf for taf in values if taf.station_id.lower() in map(str.lower, stations)]
        else:
            tafs = list(values)
        return tafs[offset:offset + limit]