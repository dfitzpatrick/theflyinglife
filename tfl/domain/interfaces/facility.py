from abc import ABC, abstractmethod

from tfl.domain.facilities import Airport


class IAirportRepository(ABC):

    @abstractmethod
    async def find(self, icao: str) -> Airport:
        pass

    @abstractmethod
    async def create(self, airport: Airport) -> None:
        pass

    @abstractmethod
    async def update(self, airport: Airport) -> Airport:
        pass

    @abstractmethod
    async def delete(self, icao: str) -> None:
        pass