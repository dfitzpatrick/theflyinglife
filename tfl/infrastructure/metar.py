from typing import Optional, Dict

from aioredis import Redis

from tfl.domain.weather import Metar
from tfl.domain.exceptions import EntityExistsError, EntityNotFoundError
from tfl.domain.interfaces.weather import IMetarRepository
import aioredis

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
        try:
            del self.repo[metar.station_id.lower()]
        except KeyError:
            raise EntityNotFoundError(f"{icao} not found.")

    async def longest_metars(self, max_number: int) -> list[Metar]:
        return sorted(self.repo.values(), key=lambda metar: len(metar.raw_text), reverse=True)[:max_number]

class MetarRedisRepository(IMetarRepository):

    def __init__(self):
        self.session: Redis = aioredis.from_url("redis://localhost")
        self.key = 'metars'

    async def find(self, icao: str) -> Metar:
        try:
            return self.session.hget()
        except KeyError:
            raise EntityNotFoundError(f"{icao} not found.")

    async def create(self, metar: Metar) -> None:
        icao = metar.station_id.lower()
        if icao in await self.session.get(self.key):
            raise EntityExistsError(f"{icao} already in repository")
        self.session[self.key][icao] = metar

    async def update(self, metar: Metar) -> Metar:
        try:
            self.session[self.key][metar.station_id.lower()] = metar
        except KeyError:
            raise EntityNotFoundError(f"{metar.station_id} not found.")

    async def delete(self, metar: Metar) -> None:
        try:
            del self.session[self.key][metar.station_id.lower()]
        except KeyError:
            raise EntityNotFoundError(f"{icao} not found.")