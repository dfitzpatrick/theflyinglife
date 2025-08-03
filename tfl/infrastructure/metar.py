from typing import Optional, Dict


from tfl.domain.weather import Metar
from tfl.domain.exceptions import EntityExistsError, EntityNotFoundError
from tfl.domain.interfaces.weather import IMetarRepository
from typing import Any
class MetarRepository(IMetarRepository):

    def __init__(self):
        self.repo: Dict[str, Metar] = {}

    async def create(self, metar: Metar) -> None:
        icao = metar.station_id.lower()
        if icao in self.repo.keys():
            raise EntityExistsError(f"{icao} already in repository")
        self.repo[icao] = metar

    async def update(self, metar: Metar):
        try:
            self.repo[metar.station_id.lower()] = metar
        except KeyError:
            raise EntityNotFoundError(f"{metar.station_id} not found.")

    async def find(self, icao: str) -> Optional[Metar]:
        try:
            return self.repo[icao.lower()]
        except KeyError:
            raise EntityNotFoundError(f"{icao} not found.")

    async def delete(self, metar: Metar) -> None:
        icao = metar.station_id.lower()
        try:
            del self.repo[icao]
        except KeyError:
            raise EntityNotFoundError(f"{icao} not found.")

    async def longest_metars(self, max_number: int) -> list[Metar]:
        return sorted(self.repo.values(), key=lambda metar: len(metar.raw_text), reverse=True)[:max_number]

    async def all(self, offset: int = 0, limit: int = 50, stations: str | None = None, sorting: tuple[Any, bool] | None = None):
        """
        Return all Metars in the repository, paginated.
        """
        values = sorted(self.repo.values(), key=sorting[0], reverse=sorting[1]) if sorting else self.repo.values()
        if stations:
            stations = stations.split(',')
            metars = [metar for metar in values if metar.station_id.lower() in map(str.lower, stations)]
        else:
            metars = list(values)
        return metars[offset:offset + limit]
    