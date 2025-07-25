from tfl.application_services.auth import AuthService
from tfl.application_services.dtpp import DTPPService
from tfl.application_services.member import MemberService
from tfl.application_services.metar import MetarService
from tfl.application_services.taf import TafService
from tfl.application_services.dcs import ChartSupplementService
from tfl.infrastructure.airport import AirportRepository
from tfl.infrastructure.member import InMemoryMemberRepository
from tfl.infrastructure.metar import MetarRepository
from tfl.infrastructure.taf import TAFRepository
from passlib.context import CryptContext
from .configuration import DATA_DIR
import pathlib
import logging

log = logging.getLogger(__name__)

password_handler = CryptContext(schemes=["bcrypt"], deprecated="auto")
taf_repository = TAFRepository()
metar_repository = MetarRepository()
member_repository = InMemoryMemberRepository()
metar_service = MetarService(metar_repository)
taf_service = TafService(taf_repository)
member_service = MemberService(member_repository, password_handler)
auth_service = AuthService(member_repository, password_handler)
airport_repository = AirportRepository()
dtpp_service = DTPPService(DATA_DIR)
dcs_path = (pathlib.Path(__file__).parents[1] / 'data').resolve()
dcs_service = ChartSupplementService(dcs_path)
