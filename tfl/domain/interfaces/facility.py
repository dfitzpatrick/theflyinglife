from abc import abstractmethod, ABC

from tfl.domain.facilities import Airport


class IAirportRepository(ABC):

    @abstractmethod
    async def find(self, icao: str) -> Airport:
        pass

    @abstractmethod
    async def create(self, airport: Airport) -> None:
        pass
