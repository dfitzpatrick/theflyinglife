import json
import pathlib
from typing import Optional, Dict, List

from tfl.domain.exceptions import EntityExistsError, EntityNotFoundError
from tfl.domain.facilities import Airport
from tfl.domain.interfaces.facility import IAirportRepository
import logging
log = logging.getLogger(__name__)
BASE_DIR = pathlib.Path(__file__).parent.resolve()
AIRPORTS_PATH = BASE_DIR.parents[1].resolve() / "data/airports.json"

def load_airport_data(path) -> Dict[str, Airport]:

    container = {}
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for icao, attrs in data.items():
            airport = Airport(**attrs)
            container[icao] = airport
    return container



class AirportRepository(IAirportRepository):


    def __init__(self):
        blah = AIRPORTS_PATH
        self.repo: Dict[str, Airport] = load_airport_data(AIRPORTS_PATH)

    async def create(self, airport: Airport) -> None:
        icao = airport.icao.upper()
        if icao in self.repo.keys():
            raise EntityExistsError(f"{icao} already in repository")
        self.repo[icao] = airport

    async def update(self, airport: Airport):
        try:
            self.repo[airport.icao.lower()] = airport
        except KeyError:
            raise EntityNotFoundError(f"{airport.icao} not found.")

    async def find(self, icao: str) -> Optional[Airport]:
        try:
            return self.repo[icao.upper()]
        except KeyError:
            raise EntityNotFoundError(f"{icao} not found.")

    async def delete(self, icao: str) -> None:
        try:
            del self.repo[icao]
        except KeyError:
            raise EntityNotFoundError(f"{icao} not found.")