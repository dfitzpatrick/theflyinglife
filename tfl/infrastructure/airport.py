import json
import pathlib
from typing import Optional, Dict, List

from tfl.domain.exceptions import EntityExistsError, EntityNotFoundError
from tfl.domain.facilities import Airport, FAAPlate
from tfl.domain.interfaces.facility import IAirportRepository
import logging

from tfl.domain.services.dtpp import load_raw_plate_data

log = logging.getLogger(__name__)
BASE_DIR = pathlib.Path(__file__).parent.resolve()
AIRPORTS_PATH = BASE_DIR.parents[1].resolve() / "data/airports.json"
TPP_PATH = BASE_DIR.parents[1].resolve() / "data/d-tpp_Metafile.xml"

def load_airport_data(path, plates=None) -> Dict[str, Airport]:
    plates = plates if plates is not None else {}
    container = {}
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for icao, attrs in data.items():
            p = plates.get(icao.upper(), [])
            airport = Airport(**attrs, plates=p)

            container[icao.upper()] = airport
    return container


def enforce_list(item):
    if not isinstance(item, list):
        return [item]
    return item


def parse_raw_plate_data(path: pathlib.Path) -> Dict[str, List[FAAPlate]]:
    container = {}
    d = load_raw_plate_data(path)
    cycle = d['digital_tpp']['@cycle']
    for state_obj in enforce_list(d['digital_tpp']['state_code']):
        for city in enforce_list(state_obj['city_name']):
            airport = city['airport_name']
            # why is this data like this?
            if isinstance(airport, list):
                for o in enforce_list(airport):
                    icao = o['@icao_ident']
                    icao = icao.upper()
                    if icao not in container.keys():
                        container[icao] = []
                    for r in enforce_list(o['record']):
                        if not isinstance(r, dict):
                            continue
                        plate = FAAPlate(
                            tpp_cycle=cycle,
                            icao=icao,
                            code=r['chart_code'],
                            name=r['chart_name'],
                            pdf_name=r['pdf_name']
                        )
                        container[icao].append(plate)
            else:
                icao = city['airport_name']['@icao_ident']
                icao = icao.upper()
                if icao not in container.keys():
                    container[icao] = []
                for r in enforce_list(city['airport_name']['record']):
                    if not isinstance(r, dict):
                        continue
                    plate = FAAPlate(
                        tpp_cycle=cycle,
                        icao=icao,
                        code=r['chart_code'],
                        name=r['chart_name'],
                        pdf_name=r['pdf_name']
                    )
                    container[icao].append(plate)
    return container


class AirportRepository(IAirportRepository):


    def __init__(self):
        blah = AIRPORTS_PATH
        self.repo: Dict[str, Airport] = load_airport_data(AIRPORTS_PATH)

    def load_dtpp(self, path: pathlib.Path):
        dtpp = parse_raw_plate_data(path)
        for icao, plates in dtpp.items():
            if icao in self.repo.keys():
                self.repo[icao].plates = plates
        log.info("DTPP Plate Data loaded to Airport Repository")


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

    async def all(self) -> List[Airport]:
        return list(self.repo.values())