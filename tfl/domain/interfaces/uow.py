from abc import ABC, abstractmethod
from tfl.domain.interfaces.members import IMemberRepository
from tfl.domain.interfaces.weather import IMetarRepository, ITAFRepository


class IUnitOfWork:
    members: IMemberRepository
    metar: IMetarRepository
    taf: ITAFRepository

    @abstractmethod
    async def commit(self):
        raise NotImplemented

    @abstractmethod
    async def rollback(self):
        raise NotImplemented

    async def __exit__(self, exc_type, exc_val, exc_tb):
        await self.rollback()
