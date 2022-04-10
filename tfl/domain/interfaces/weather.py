from asyncio import Protocol

from tfl.domain.facilities import Airport
from tfl.domain.weather import Metar, TAF
from abc import ABC, abstractmethod





class IFacilityWeather(Protocol):

    async def taf(self, icao: str) -> TAF:
        ...

    async def metar(self, icao: str) -> Metar:
        ...



class IMetarRepository(ABC):

    @abstractmethod
    async def find(self, icao: str) -> Metar:
        pass

    @abstractmethod
    async def create(self, metar: Metar) -> None:
        pass

    @abstractmethod
    async def update(self, metar: Metar) -> Metar:
        pass

    @abstractmethod
    async def delete(self, metar: Metar) -> None:
        pass


class ITAFRepository(ABC):

    @abstractmethod
    async def find(self, icao: str) -> TAF:
        pass

    @abstractmethod
    async def create(self, taf: TAF) -> None:
        pass

    @abstractmethod
    async def update(self, taf: TAF) -> TAF:
        pass

    @abstractmethod
    async def delete(self, taf: TAF) -> None:
        pass


