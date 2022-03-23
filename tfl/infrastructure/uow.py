from tfl.domain.interfaces.uow import IUnitOfWork
from tfl.infrastructure.member import InMemoryMemberRepository
from tfl.infrastructure.metar import MetarRepository
from tfl.infrastructure.taf import TAFRepository


class UnitOfWork(IUnitOfWork):

    def __init__(self):
        self.members = InMemoryMemberRepository()
        self.metar = MetarRepository()
        self.taf = TAFRepository()

    async def commit(self):
        pass

    async def rollback(self):
        pass

    def __enter__(self):
