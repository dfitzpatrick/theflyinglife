from tfl.application_services.adds import ADDSPolling
from tfl.application_services.auth import AuthService
from tfl.application_services.member import MemberService
from tfl.application_services.metar import MetarService
from tfl.application_services.taf import TafService
from tfl.infrastructure.member import InMemoryMemberRepository
from tfl.infrastructure.metar import MetarRepository, MetarRedisRepository
from tfl.infrastructure.taf import TAFRepository
from passlib.context import CryptContext

password_handler = CryptContext(schemes=["bcrypt"], deprecated="auto")
taf_repository = TAFRepository()
metar_repository = MetarRepository()
member_repository = InMemoryMemberRepository()
metar_service = MetarService(metar_repository)
taf_service = TafService(taf_repository)
member_service = MemberService(member_repository, password_handler)
auth_service = AuthService(member_repository, password_handler)
